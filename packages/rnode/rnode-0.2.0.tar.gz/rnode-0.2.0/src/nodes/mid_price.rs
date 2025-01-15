use std::sync::Arc;
use tokio::sync::{RwLock, Mutex};
use crate::error::*;
use crate::ws_client::WsClient;
use crate::types::*;
use crate::utils::*;
use tracing::{error, debug};
use pyo3::prelude::*;
use std::collections::HashMap;
use tokio::sync::broadcast;

pub struct MidPriceNode {
    instruments: HashMap<String, InstrumentData>,
    ws_client: Arc<WsClient>,
    price_sender: Arc<broadcast::Sender<(String, f64, i64)>>,
}

#[derive(Clone)]
struct InstrumentData {
    last_exchange_time: Arc<RwLock<i64>>,
    status: Arc<RwLock<DataStatus>>,
    current_data: Arc<RwLock<MidPriceData>>,
    interval_manager: Arc<RwLock<IntervalManager>>,
    sending_lock: Arc<Mutex<()>>,
    current_period: Arc<RwLock<i64>>,
}

// 添加一个辅助函数来解析数值
fn parse_number(value: &serde_json::Value) -> Option<f64> {
    match value {
        serde_json::Value::String(s) => s.parse::<f64>().ok(),
        serde_json::Value::Number(n) => n.as_f64(),
        _ => None,
    }
}

impl MidPriceNode {
    pub fn new(freq: String, instrument_ids: Vec<String>, ws_client: Arc<WsClient>) -> Self {
        let (price_sender, _) = broadcast::channel(10000);
        let price_sender = Arc::new(price_sender);
        let mut instruments = HashMap::new();
        
        for instrument_id in instrument_ids {
            instruments.insert(instrument_id.clone(), InstrumentData {
                last_exchange_time: Arc::new(RwLock::new(0)),
                current_data: Arc::new(RwLock::new(MidPriceData {
                    exchange_time: 0,
                    mid_prc: 0.0,
                })),
                status: Arc::new(RwLock::new(DataStatus::Empty)),
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
            price_sender,
        }
    }

    async fn send_data(
        data: &mut MidPriceData,
        status: &DataStatus,
        instrument_id: &str,
        callback: &PyObject,
        current_time: i64,
        sending_lock: &Mutex<()>,
        current_period: &RwLock<i64>,
        period_id: i64,
    ) -> bool {
        let _lock = sending_lock.lock().await;
        
        let mut period = current_period.write().await;
        if *period >= period_id {
            return false;
        }
        
        // 检查回调是否为 None
        Python::with_gil(|py| {
            if callback.as_ref(py).is_none() {
                return;  // 如果是 None，直接返回
            }
            
            if data.exchange_time > 0 {
                let response = serde_json::json!({
                    "type": "mid_price",
                    "instrument_id": instrument_id,
                    "data": {
                        "exchange_time": data.exchange_time,
                        "mid_price": data.mid_prc,
                    },
                    "status":status,
                    "timestamp": current_time
                });
                
                if let Err(e) = callback.call1(py, (serde_json::to_string(&response).unwrap(),)) {
                    error!("Callback failed: {:?}", e);
                }
            } else {
                let response = serde_json::json!({
                    "type": "mid_price",
                    "instrument_id": instrument_id,
                    "data": null,
                    "status": DataStatus::Invalid,
                    "timestamp": current_time
                });
                
                if let Err(e) = callback.call1(py, (serde_json::to_string(&response).unwrap(),)) {
                    error!("Callback failed: {:?}", e);
                }
            }
        });
        
        // 重置数据
        if data.exchange_time > 0 {
            data.exchange_time = 0;
            data.mid_prc = 0.0;
        }
        
        *period = period_id;
        true
    }

    pub async fn start(&self, callback: PyObject) -> Result<()> {
        // 订阅所有 instrument 的数据
        for instrument_id in self.instruments.keys() {
            debug!("Subscribing to BBO data for {}", instrument_id);
            self.ws_client.subscribe(DmsEventType::BBO, instrument_id).await?;
        }
        
        // 获取接收器
        let mut receiver = self.ws_client.get_receiver();
        
        // 克隆需要在异步闭包中使用的数据
        let instruments = self.instruments.clone();
        let callback = callback.clone();
        let price_sender = self.price_sender.clone();
        let price_sender_clone = price_sender.clone();  // 用于检查接收者

        let ws_client = self.ws_client.clone();
        tokio::spawn(async move {
            while let Ok(msg) = receiver.recv().await {
                for (instrument_id, data) in instruments.iter() {
                    if let Ok(msg_json) = serde_json::from_str::<serde_json::Value>(&msg) {
                        if let Some(topic) = msg_json["topic"].as_str() {
                            if topic == format!("bbo.{}", instrument_id) {
                                if let Ok(bbo_data) = serde_json::from_str::<serde_json::Value>(&msg) {
                                    let exchange_time = bbo_data["tt"].as_i64().unwrap_or(0);
                                    let exchange_time_ms = exchange_time / 1000;
                                    
                                    // 检查时间有效性
                                    let last_time = *data.last_exchange_time.read().await;
                                    if exchange_time < last_time {
                                        debug!("Skipping outdated BBO data for {}", instrument_id);
                                        continue;
                                    }

                                    // 使用克隆的 ws_client
                                    ws_client.update_time().await;
                                    let current_time = ws_client.get_current_time().await;

                                    if exchange_time_ms > current_time {
                                        debug!("Skipping future BBO data for {} {} {}", instrument_id, exchange_time_ms, current_time);
                                        continue;
                                    }
                                    // 更新数据
                                    if let Some(body) = bbo_data["body"].as_array() {
                                        if body.len() >= 2 {
                                            // 解析卖方(Ask)数据
                                            let ask = &body[0];
                                            let ask_price = parse_number(&ask[0]).unwrap_or(0.0);
                                            let ask_qty = parse_number(&ask[1]).unwrap_or(0.0);
                                            let _ask_base_size = parse_number(&ask[2]).unwrap_or(0.0);
                                                
                                            // 解析买方(Bid)数据
                                            let bid = &body[1];
                                            let bid_price = parse_number(&bid[0]).unwrap_or(0.0);
                                            let bid_qty = parse_number(&bid[1]).unwrap_or(0.0);
                                            let _bid_base_size = parse_number(&bid[2]).unwrap_or(0.0);

                                            // 检查时间单调性
                                            let last_time = *data.last_exchange_time.read().await;
                                            let mut current = data.current_data.write().await;
                                            let status = if exchange_time < last_time {
                                                DataStatus::NonMono
                                            } else if ask_price <= bid_price {
                                                // 检查价格交叉
                                                DataStatus::CrossPrice
                                            } else if ask_qty == 0.0 && bid_qty == 0.0 {
                                                // 没有报价量
                                                DataStatus::InvalidQty
                                            } else if ask_qty == 0.0 {
                                                // 只有买方报价
                                                current.mid_prc = 0.5 * bid_price;
                                                DataStatus::OnewayQuote
                                            } else if bid_qty == 0.0 {
                                                // 只有卖方报价
                                                current.mid_prc = ask_price + 0.5 * (ask_price - bid_price);
                                                DataStatus::OnewayQuote
                                            } else {
                                                // 正常情况
                                                current.mid_prc = (ask_price + bid_price) / 2.0;
                                                DataStatus::BasicValid
                                            };

                                            // 更新数据
                                            current.exchange_time = exchange_time_ms;
                                            *data.last_exchange_time.write().await = exchange_time;
                                            *data.status.write().await = status.clone();

                                            // 只在有接收者时才发送最新的中间价
                                            if price_sender_clone.receiver_count() > 0 {
                                                if let Err(e) = price_sender.send((
                                                    instrument_id.clone(),
                                                    current.mid_prc,
                                                    exchange_time
                                                )) {
                                                    if !e.to_string().contains("no receivers") {
                                                        error!("Failed to broadcast mid price: {}", e);
                                                    }
                                                }
                                            }

                                            // 检查是否需要发送数据
                                            let mut manager = data.interval_manager.write().await;
                                            if manager.should_advance(exchange_time_ms) {
                                                let period_id = manager.get_current_period();
                                                if Self::send_data(
                                                    &mut current,
                                                    &status,
                                                    instrument_id,
                                                    &callback,
                                                    current_time,
                                                    &data.sending_lock,
                                                    &data.current_period,
                                                    period_id,
                                                ).await {
                                                    manager.advance();
                                                }
                                            }
                                        }
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

    pub fn subscribe_price(&self) -> broadcast::Receiver<(String, f64, i64)> {
        let receiver = self.price_sender.subscribe();
        receiver
    }
} 