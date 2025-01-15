use crate::types::*;
use crate::error::*;
use crate::replay::{MasterClock, ReplayConfig};
use futures::{SinkExt, StreamExt};
use std::sync::Arc;
use tokio::sync::{broadcast, Mutex};
use tokio_tungstenite::{connect_async, WebSocketStream, MaybeTlsStream};
use tokio_tungstenite::tungstenite::Message;
use tracing::{info, error, warn, debug};
use std::time::Duration;
use tokio::time::sleep;
use tokio::task::JoinHandle;
use chrono::Utc;

type WsStream = WebSocketStream<MaybeTlsStream<tokio::net::TcpStream>>;

pub struct WsClient {
    url: String,
    sender: Arc<broadcast::Sender<String>>,
    subscriptions: Arc<Mutex<Vec<(DmsEventType, String)>>>,
    write_stream: Arc<Mutex<Option<futures::stream::SplitSink<WsStream, Message>>>>,
    is_connected: Arc<Mutex<bool>>,
    reconnect_handle: Arc<Mutex<Option<JoinHandle<()>>>>,
    replay_config: Option<ReplayConfig>,
    master_clock: Option<Arc<MasterClock>>,
    is_replay: bool,
}

impl WsClient {
    pub fn new(url: String) -> Self {
        let (sender, _) = broadcast::channel(1000);
        Self {
            url,
            sender: Arc::new(sender),
            subscriptions: Arc::new(Mutex::new(Vec::new())),
            write_stream: Arc::new(Mutex::new(None)),
            is_connected: Arc::new(Mutex::new(false)),
            reconnect_handle: Arc::new(Mutex::new(None)),
            replay_config: None,
            master_clock: None,
            is_replay: false,
        }
    }

    pub fn with_replay(
        url: String,
        start_time: i64,
        end_time: i64,
        speed_multiplier: f64,
        replay_window: i64,
        x_cur_time: i64,
    ) -> Self {
        let replay_config = ReplayConfig::new(
            start_time * 1000,
            end_time * 1000,
            speed_multiplier,
            replay_window,
            x_cur_time / 1000,
        );
        
        let master_clock = MasterClock::new(start_time, speed_multiplier);
        
        let mut client = Self::new(url);
        client.replay_config = Some(replay_config);
        client.master_clock = Some(Arc::new(master_clock));
        client.is_replay = true;
        client
    }

    pub async fn connect(&self) -> Result<()> {
        let max_retries = 3;
        let mut retry_count = 0;
        
        while retry_count < max_retries {
            info!("Connecting to {} (attempt {}/{})", self.url, retry_count + 1, max_retries);
            
            match self.try_connect().await {
                Ok(_) => {
                    info!("Connection established successfully");
                    return Ok(());
                }
                Err(e) => {
                    error!("Connection failed: {}", e);
                    retry_count += 1;
                    if retry_count < max_retries {
                        tokio::time::sleep(Duration::from_secs(5)).await;
                    }
                }
            }
        }
        
        Err(MarketDataError::WebSocketError("Failed to connect after max retries".to_string()))
    }

    async fn try_connect(&self) -> Result<()> {
        info!("Connecting to {}", self.url);
        let url = url::Url::parse(&self.url)
            .map_err(|e| MarketDataError::WebSocketError(e.to_string()))?;
            
        let (ws_stream, response) = connect_async(url).await
            .map_err(|e| MarketDataError::WebSocketError(e.to_string()))?;
            
        info!("WebSocket connected with response: {:?}", response);

        let (write, read) = ws_stream.split();
        *self.write_stream.lock().await = Some(write);
        *self.is_connected.lock().await = true;
        
        let sender = self.sender.clone();
        let is_connected = self.is_connected.clone();
        let write_stream = self.write_stream.clone();
        let url = self.url.clone();
        let subscriptions = self.subscriptions.clone();
        
        let handle = tokio::spawn(async move {
            info!("Starting message handler task");
            Self::handle_messages(read, sender.clone(), is_connected.clone()).await;
            
            *is_connected.lock().await = false;
            error!("Connection lost, attempting to reconnect...");
            
            // 开始重连过程
            let mut attempt = 0;
            let max_attempts = 20;
            let retry_interval = Duration::from_secs(2);
            
            while attempt < max_attempts {
                attempt += 1;
                info!("Reconnection attempt {}/{}", attempt, max_attempts);
                
                match Self::reconnect_with_subscriptions(
                    &url,
                    &write_stream,
                    &is_connected,
                    &subscriptions
                ).await {
                    Ok(_) => {
                        info!("Successfully reconnected");
                        break;
                    }
                    Err(e) => {
                        error!("Reconnection attempt {} failed: {}", attempt, e);
                        if attempt < max_attempts {
                            sleep(retry_interval).await;
                        }
                    }
                }
            }
            
            if attempt >= max_attempts {
                error!("Failed to reconnect after {} attempts", max_attempts);
            }
        });

        *self.reconnect_handle.lock().await = Some(handle);
        Ok(())
    }

    async fn reconnect_with_subscriptions(
        url: &str,
        write_stream: &Arc<Mutex<Option<futures::stream::SplitSink<WsStream, Message>>>>,
        is_connected: &Arc<Mutex<bool>>,
        subscriptions: &Arc<Mutex<Vec<(DmsEventType, String)>>>,
    ) -> Result<()> {
        // 建立新连接
        let url = url::Url::parse(url)
            .map_err(|e| MarketDataError::WebSocketError(e.to_string()))?;
            
        let (ws_stream, _) = connect_async(url).await
            .map_err(|e| MarketDataError::WebSocketError(e.to_string()))?;
            
        let (write, _) = ws_stream.split();
        *write_stream.lock().await = Some(write);
        *is_connected.lock().await = true;

        // 重新发送所有订阅
        let subs = subscriptions.lock().await.clone();
        if let Some(write) = &mut *write_stream.lock().await {
            for (event_type, instrument_id) in subs {
                let subscription = serde_json::json!({
                    "event": "sub",
                    "topic": format!("{}.{}", event_type, instrument_id)
                });
                
                debug!("Resubscribing to {}.{}", event_type, instrument_id);
                write.send(Message::Text(subscription.to_string())).await
                    .map_err(|e| MarketDataError::WebSocketError(e.to_string()))?;
            }
        }

        Ok(())
    }

    pub async fn send_message(&self, message: &str) -> Result<()> {
        let is_connected = *self.is_connected.lock().await;
        if !is_connected {
            return Err(MarketDataError::WebSocketError("Not connected".to_string()));
        }

        let mut write_lock = self.write_stream.lock().await;
        if let Some(write) = &mut *write_lock {
            info!("Sending message: {}", message);
            write.send(Message::Text(message.to_string())).await
                .map_err(|e| MarketDataError::WebSocketError(e.to_string()))?;
            Ok(())
        } else {
            Err(MarketDataError::WebSocketError("Write stream not initialized".to_string()))
        }
    }

    async fn handle_messages(
        mut read: futures::stream::SplitStream<WsStream>,
        sender: Arc<broadcast::Sender<String>>,
        is_connected: Arc<Mutex<bool>>,
    ) {
        info!("Message handler started");

        while let Some(message) = read.next().await {
            match message {
                Ok(Message::Text(text)) => {
                    match sender.send(text.clone()) {
                        Ok(_) => {}
                        Err(e) => {
                            if e.to_string() != "channel closed" {
                                error!("Failed to forward message: {}", e);
                            }
                        }
                    }
                }
                Ok(Message::Close(_)) => {
                    warn!("Received close frame");
                    break;
                }
                Err(e) => {
                    error!("WebSocket error: {}", e);
                    break;
                }
                _ => {}
            }
        }

        warn!("Message handler stopping");
        *is_connected.lock().await = false;
    }

    pub async fn subscribe(&self, event_type: DmsEventType, instrument_id: &str) -> Result<()> {
        let mut subscriptions = self.subscriptions.lock().await;
        subscriptions.push((event_type.clone(), instrument_id.to_string()));
        
        if *self.is_connected.lock().await {
            self.send_subscription(event_type, instrument_id).await?;
        }
        
        Ok(())
    }

    pub fn get_receiver(&self) -> broadcast::Receiver<String> {
        self.sender.subscribe()
    }

    pub async fn send_subscription(&self, event_type: DmsEventType, instrument_id: &str) -> Result<()> {
        let mut subscription = serde_json::json!({
            "event": "sub",
            "topic": format!("{}.{}", event_type, instrument_id)
        });
        debug!("Sending subscription: {}", subscription);

        // 如果是回放模式，添加回放参数
        if let Some(replay_config) = &self.replay_config {
            let replay_params = replay_config.to_subscription_params();
            subscription.as_object_mut().unwrap()
                .extend(replay_params.as_object().unwrap().clone());
        }
        
        self.send_message(&subscription.to_string()).await
    }

    pub async fn close(&self) -> Result<()> {
        if *self.is_connected.lock().await {
            let mut write_lock = self.write_stream.lock().await;
            if let Some(write) = &mut *write_lock {
                write.close().await
                    .map_err(|e| MarketDataError::WebSocketError(e.to_string()))?;
                info!("Connection closed");
                Ok(())
            } else {
                Err(MarketDataError::WebSocketError("Not connected".to_string()))
            }
        } else {
            Ok(()) // 已经关闭了
        }
    }

    pub async fn get_current_time(&self) -> i64 {
        if self.is_replay {
            if let Some(master_clock) = &self.master_clock {
                master_clock.get_current_time().await
            } else {
                Utc::now().timestamp_millis()
            }
        } else {
            Utc::now().timestamp_millis()
        }
    }

    pub async fn update_time(&self) {
        if let Some(master_clock) = &self.master_clock {
            master_clock.update_time().await;
        }
    }
} 