use std::sync::Arc;
use tokio::sync::{RwLock, Mutex, broadcast};
use tokio::time::Duration;
use crate::error::*;
use crate::ws_client::WsClient;
use crate::types::*;
use crate::utils::*;
use tracing::debug;
use pyo3::prelude::*;
use std::collections::HashMap;

pub struct TotalVolumeNode {
    instruments: HashMap<String, InstrumentData>,
    ws_client: Arc<WsClient>,
    volume_sender: Arc<broadcast::Sender<TotalVolumeData>>,
}

#[derive(Clone)]
struct InstrumentData {
    last_exchange_time: Arc<RwLock<i64>>,
    current_data: Arc<RwLock<TotalVolumeData>>,
    interval_manager: Arc<RwLock<IntervalManager>>,
    sending_lock: Arc<Mutex<()>>,
    current_period: Arc<RwLock<i64>>,
}

fn parse_number(value: &serde_json::Value) -> Option<f64> {
    match value {
        serde_json::Value::String(s) => s.parse::<f64>().ok(),
        serde_json::Value::Number(n) => n.as_f64(),
        _ => None,
    }
}

impl TotalVolumeNode {
    pub fn new(freq: String, instrument_ids: Vec<String>, ws_client: Arc<WsClient>) -> Self {
        let (volume_sender, _) = broadcast::channel(10000);
        let volume_sender = Arc::new(volume_sender);
        let mut instruments = HashMap::new();
        
        for instrument_id in instrument_ids {
            instruments.insert(instrument_id.clone(), InstrumentData {
                last_exchange_time: Arc::new(RwLock::new(0)),
                current_data: Arc::new(RwLock::new(TotalVolumeData::default())),
                interval_manager: Arc::new(RwLock::new(IntervalManager::new(
                    freq.clone(),
                    ws_client.clone(),
                ).expect("Invalid frequency"))),
                sending_lock: Arc::new(Mutex::new(())),
                current_period: Arc::new(RwLock::new(0)),
            });
        }
        
        Self {
            instruments,
            ws_client,
            volume_sender,
        }
    }

    pub fn subscribe_volume(&self) -> broadcast::Receiver<TotalVolumeData> {
        let receiver = self.volume_sender.subscribe();
        receiver
    }

    async fn send_data(
        data: &mut TotalVolumeData,
        instrument_id: &str,
        callback: &PyObject,
        current_time: i64,
        sending_lock: &Mutex<()>,
        current_period: &RwLock<i64>,
        period_id: i64,
        volume_sender: &broadcast::Sender<TotalVolumeData>,
    ) -> bool {
        let _lock = sending_lock.lock().await;
        
        let mut period = current_period.write().await;
        if *period >= period_id {
            return false;
        }
        
        if data.exchange_time > 0 {
            // 克隆数据用于广播
            let mut current_clone = data.clone();
            current_clone.period_id = period_id;
            if let Err(e) = volume_sender.send(current_clone) {
                if !e.to_string().contains("no receivers") {
                    debug!("Failed to broadcast volume data: {}", e);
                }
            }

            // 检查回调是否为 None
            Python::with_gil(|py| {
                if !callback.as_ref(py).is_none() {
                    let response = serde_json::json!({
                        "type": "total_volume",
                        "instrument_id": instrument_id,
                        "data": {
                            "exchange_time": data.exchange_time,
                            "total_volume": data.total_volume,
                            "taker_buy_volume": data.taker_buy_base_asset_volume,
                            "number_of_trades": data.number_of_trades,
                        },
                        "status": DataStatus::BasicValid,
                        "timestamp": current_time
                    });
                    
                    if let Err(e) = callback.call1(py, (serde_json::to_string(&response).unwrap(),)) {
                        debug!("Callback failed: {:?}", e);
                    }
                }
            });
            
            *data = TotalVolumeData::default();
        } else {
            // 检查回调是否为 None
            Python::with_gil(|py| {
                if !callback.as_ref(py).is_none() {
                    let response = serde_json::json!({
                        "type": "total_volume",
                        "instrument_id": instrument_id,
                        "data": null,
                        "status": DataStatus::Invalid,
                        "timestamp": current_time
                    });
                    
                    if let Err(e) = callback.call1(py, (serde_json::to_string(&response).unwrap(),)) {
                        debug!("Callback failed: {:?}", e);
                    }
                }
            });
        }
        
        *period = period_id;
        true
    }

    pub async fn start(&self, callback: PyObject) -> Result<()> {
        // 订阅所有 instrument 的数据
        for instrument_id in self.instruments.keys() {
            self.ws_client.subscribe(DmsEventType::TRADE, instrument_id).await?;
        }
        
        // 获取接收器
        let mut receiver = self.ws_client.get_receiver();
        
        // 为每个 instrument 启动定时器任务
        for (instrument_id, data) in &self.instruments {
            let timer_callback = callback.clone();
            let timer_data = data.current_data.clone();
            let timer_manager = data.interval_manager.clone();
            let sending_lock = data.sending_lock.clone();
            let current_period = data.current_period.clone();
            let instrument_id = instrument_id.clone();
            let volume_sender_clone = self.volume_sender.clone();
            
            let ws_client = self.ws_client.clone();
            tokio::spawn(async move {
                let mut interval = tokio::time::interval(Duration::from_secs(1));
                loop {
                    interval.tick().await;
                    ws_client.update_time().await;
                    let current_time = ws_client.get_current_time().await;
                    
                    let mut manager = timer_manager.write().await;
                    if manager.should_advance(current_time) {
                        let period_id = manager.get_current_period();
                        let mut data = timer_data.write().await;
                        if Self::send_data(
                            &mut data,
                            &instrument_id,
                            &timer_callback,
                            current_time,
                            &sending_lock,
                            &current_period,
                            period_id,
                            &volume_sender_clone,
                        ).await {
                            manager.advance();
                        }
                    }
                }
            });
        }

        // 消息处理任务
        let instruments = self.instruments.clone();
        let callback = callback.clone();
        let volume_sender = self.volume_sender.clone();
        let ws_client = self.ws_client.clone();

        tokio::spawn(async move {
            while let Ok(msg) = receiver.recv().await {
                for (instrument_id, data) in instruments.iter() {
                    if let Ok(msg_json) = serde_json::from_str::<serde_json::Value>(&msg) {
                        if let Some(topic) = msg_json["topic"].as_str() {
                            if topic == format!("trade.{}", instrument_id) {
                                if let Ok(trade_data) = serde_json::from_str::<serde_json::Value>(&msg) {
                                    let exchange_time = trade_data["tt"].as_i64().unwrap_or(0);
                                    let exchange_time_ms = exchange_time / 1000;
                                    
                                    // 检查时间有效性
                                    let last_time = *data.last_exchange_time.read().await;
                                    if exchange_time < last_time {
                                        debug!("Skipping outdated trade data for {}", instrument_id);
                                        continue;
                                    }

                                    // 使用 ws_client 获取当前时间
                                    ws_client.update_time().await;
                                    let current_time = ws_client.get_current_time().await;

                                    if exchange_time_ms > current_time {
                                        debug!("Skipping future trade data for {}", instrument_id);
                                        continue;
                                    }

                                    let mut manager = data.interval_manager.write().await;
                                    let period_id = manager.get_current_period();
                                    if manager.should_advance(exchange_time_ms) {
                                        let mut current = data.current_data.write().await;
                                        if Self::send_data(
                                            &mut current,
                                            instrument_id,
                                            &callback,
                                            current_time,
                                            &data.sending_lock,
                                            &data.current_period,
                                            period_id,
                                            &volume_sender,
                                        ).await {
                                            manager.advance();
                                        }
                                    }

                                    // 更新数据
                                    if let Some(body) = trade_data["body"].as_object() {
                                        let mut current = data.current_data.write().await;
                                        let quantity = parse_number(&body["q"])
                                            .unwrap_or(0.0);
                                        let is_buy = body["d"].as_str().unwrap_or("") == "buy";
                                        
                                        current.total_volume += quantity;
                                        if is_buy {
                                            current.taker_buy_base_asset_volume += quantity;
                                        }
                                        current.number_of_trades += 1;
                                        current.exchange_time = exchange_time_ms;
                                        current.period_id = period_id;
                                        
                                        *data.last_exchange_time.write().await = exchange_time;
                                    }
                                }
                                break;
                            }
                        }
                    }
                }
            }
        });

        Ok(())
    }
} 