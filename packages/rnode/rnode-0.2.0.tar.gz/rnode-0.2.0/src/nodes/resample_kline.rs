use std::sync::Arc;
use tokio::sync::{RwLock, Mutex};
use crate::error::*;
use crate::types::*;
use crate::utils::*;
use tracing::{error, debug};
use pyo3::prelude::*;
use std::collections::HashMap;
use crate::nodes::simple_kline::SimpleKlineNode;
use crate::nodes::total_volume::TotalVolumeNode;
use crate::ws_client::WsClient;

#[derive(Debug, Clone)]
pub struct ResampleKlineData {
    pub instrument_id: String,
    pub open_time: i64,
    pub open: f64,
    pub high: f64,
    pub low: f64,
    pub close: f64,
    pub volume: f64,
    pub close_time: i64,
    pub number_of_trades: i64,
    pub taker_buy_base_asset_volume: f64,
}

pub struct ResampleKlineNode {
    instruments: HashMap<String, InstrumentData>,
    kline_nodes: HashMap<String, Arc<SimpleKlineNode>>,
    volume_nodes: HashMap<String, Arc<TotalVolumeNode>>,
    interval_manager: Arc<RwLock<IntervalManager>>,
    ws_client: Arc<WsClient>,
}

#[derive(Clone)]
struct InstrumentData {
    current_data: Arc<RwLock<ResampleKlineData>>,
    sending_lock: Arc<Mutex<()>>,
    current_period: Arc<RwLock<i64>>,
}

impl ResampleKlineNode {
    pub fn new(
        freq: String,
        instrument_ids: Vec<String>,
        kline_nodes: HashMap<String, Arc<SimpleKlineNode>>,
        volume_nodes: HashMap<String, Arc<TotalVolumeNode>>,
        ws_client: Arc<WsClient>,
    ) -> Self {
        let mut instruments = HashMap::new();
        let interval_manager = Arc::new(RwLock::new(IntervalManager::new(
            freq.clone(),
            ws_client.clone(),
        ).expect("Invalid frequency")));
        
        for instrument_id in instrument_ids {
            instruments.insert(instrument_id.clone(), InstrumentData {
                current_data: Arc::new(RwLock::new(ResampleKlineData {
                    instrument_id: instrument_id.clone(),
                    open_time: 0,
                    open: 0.0,
                    high: 0.0,
                    low: f64::MAX,
                    close: 0.0,
                    volume: 0.0,
                    close_time: 0,
                    number_of_trades: 0,
                    taker_buy_base_asset_volume: 0.0,
                })),
                sending_lock: Arc::new(Mutex::new(())),
                current_period: Arc::new(RwLock::new(0)),
            });
        }
        
        Self {
            instruments,
            kline_nodes,
            volume_nodes,
            interval_manager,
            ws_client,
        }
    }

    async fn send_data(
        data: &ResampleKlineData,
        instrument_id: &str,
        callback: &PyObject,
        current_time: i64,
        sending_lock: &Mutex<()>,
        current_period: &RwLock<i64>,
        period_id: i64,
    ) -> bool {
        let _lock = sending_lock.lock().await;
        
        let mut period = current_period.write().await;
        if *period > period_id {
            debug!("Skipping old period {} for {}, current period is {}", 
                period_id, instrument_id, *period);
            return false;
        }
        if data.close == 0.0 || data.volume == 0.0 {
            debug!("Skipping empty data for {} at period {}", instrument_id, period_id);
            return false;
        }
        
        Python::with_gil(|py| {
            if callback.as_ref(py).is_none() {
                error!("Callback is None");
                return;
            }
            
            let response = serde_json::json!({
                "type": "resample_kline",
                "instrument_id": instrument_id,
                "data": {
                    "instrument_id": data.instrument_id,
                    "open_time": data.open_time,
                    "open": data.open,
                    "high": data.high,
                    "low": data.low,
                    "close": data.close,
                    "volume": data.volume,
                    "close_time": data.close_time,
                    "number_of_trades": data.number_of_trades,
                    "taker_buy_base_asset_volume": data.taker_buy_base_asset_volume,
                },
                "status": DataStatus::BasicValid,
                "timestamp": current_time,
                "period_id": period_id  // 添加 period_id 到响应中
            });

            let json_str = serde_json::to_string(&response).unwrap();
            
            match callback.call1(py, (json_str,)) {
                Ok(_) => {}
                Err(e) => {
                    error!("Callback failed for {} at period {}: {:?}", instrument_id, period_id, e);
                    if let Some(tb) = e.traceback(py) {
                        error!("Traceback: {}", tb.format().unwrap_or_default());
                    }
                }
            }
        });
        
        *period = period_id;
        true
    }

    async fn process_kline_data(
        kline_data: &SimpleKlineData,
        current: &mut ResampleKlineData,
        current_period: i64,
        last_kline_period: i64,
    ) {
        if current_period > last_kline_period || current.open_time == 0 {
            // 新周期或首次数据
            current.open_time = kline_data.open_time;
            current.open = kline_data.open;
            current.high = kline_data.high;
            current.low = kline_data.low;
            current.close = kline_data.close;
            current.close_time = kline_data.close_time;
        } else if current_period == last_kline_period {
            // 同一周期，更新高低点和收盘价
            current.high = current.high.max(kline_data.high);
            current.low = current.low.min(kline_data.low);
            current.close = kline_data.close;
            current.close_time = kline_data.close_time;
        }
    }

    async fn process_volume_data(
        volume_data: &TotalVolumeData,
        current: &mut ResampleKlineData,
        current_period: i64,
        last_volume_period: i64,
    ) {
        
        if current_period >= last_volume_period {
            current.volume += volume_data.total_volume;
            current.number_of_trades += volume_data.number_of_trades;
            current.taker_buy_base_asset_volume += volume_data.taker_buy_base_asset_volume;
        }
    }

    pub async fn start(&self, callback: PyObject) -> Result<()> {
        let interval_manager = self.interval_manager.clone();
        let ws_client = self.ws_client.clone();
        let kline_nodes = self.kline_nodes.clone();
        let volume_nodes = self.volume_nodes.clone();
        let instruments = self.instruments.clone();
        
        // 使用 rayon 的线程池来并行处理数据
        rayon::ThreadPoolBuilder::new()
            .num_threads(num_cpus::get())
            .build_global()
            .unwrap();
        
        for (instrument_id, data) in &instruments {
            let kline_node = kline_nodes.get(instrument_id).unwrap().clone();
            let volume_node = volume_nodes.get(instrument_id).unwrap().clone();
            let data_clone = data.clone();
            let callback_clone = callback.clone();
            let instrument_id_clone = instrument_id.clone();
            let interval_manager = interval_manager.clone();
            let ws_client = ws_client.clone();

            let mut kline_receiver = kline_node.subscribe_kline();
            let mut volume_receiver = volume_node.subscribe_volume();
            
            tokio::spawn(async move {
                let mut last_kline_period = 0i64;
                let mut last_volume_period = 0i64;
                
                // 创建定时检查任务
                let check_interval = tokio::time::interval(tokio::time::Duration::from_secs(1));
                let data_clone_for_timer = data_clone.clone();
                let callback_clone_for_timer = callback_clone.clone();
                let instrument_id_clone_for_timer = instrument_id_clone.clone();
                let ws_client_for_timer = ws_client.clone();
                
                tokio::spawn(async move {
                    let mut check_interval = check_interval;
                    loop {
                        check_interval.tick().await;
                        ws_client_for_timer.update_time().await;
                        let current_time = ws_client_for_timer.get_current_time().await;
                        
                        
                        let manager = interval_manager.read().await;
                        let current_period = manager.get_period_id(current_time);
                        
                        let mut current = data_clone_for_timer.current_data.write().await;
                        let period = *data_clone_for_timer.current_period.read().await;
                        
                        // 如果当前周期比已发送的周期大，且有数据，则发送
                        if current_period > period && current.close > 0.0 && current.volume > 0.0 {
                            if Self::send_data(
                                &current,
                                &instrument_id_clone_for_timer,
                                &callback_clone_for_timer,
                                current_time,
                                &data_clone_for_timer.sending_lock,
                                &data_clone_for_timer.current_period,
                                period + 1,  // 发送下一个周期的数据
                            ).await {
                                // 重置数据
                                *current = ResampleKlineData {
                                    instrument_id: instrument_id_clone_for_timer.clone(),
                                    open_time: 0,
                                    open: 0.0,
                                    high: 0.0,
                                    low: f64::MAX,
                                    close: 0.0,
                                    volume: 0.0,
                                    close_time: 0,
                                    number_of_trades: 0,
                                    taker_buy_base_asset_volume: 0.0,
                                };
                            }
                        }
                    }
                });

                // 数据处理任务
                let ws_client_for_data = ws_client.clone();
                tokio::spawn(async move {
                    loop {
                        tokio::select! {
                            Ok(kline_data) = kline_receiver.recv() => {
                                ws_client_for_data.update_time().await;
                                let current_time = ws_client_for_data.get_current_time().await;
                                
                                
                                let current_period = kline_data.period_id;
                                let mut current = data_clone.current_data.write().await;
                                if current_period >= last_kline_period {
                                    Self::process_kline_data(&kline_data, &mut current, current_period, last_kline_period).await;
                                    last_kline_period = current_period;
                                    
                                    if last_volume_period == current_period && current.volume > 0.0 {
                                        if Self::send_data(
                                            &current,
                                            &instrument_id_clone,
                                            &callback_clone,
                                            current_time,
                                            &data_clone.sending_lock,
                                            &data_clone.current_period,
                                            current_period,
                                        ).await {
                                            // 重置数据
                                            *current = ResampleKlineData {
                                                instrument_id: instrument_id_clone.clone(),
                                                open_time: 0,
                                                open: 0.0,
                                                high: 0.0,
                                                low: f64::MAX,
                                                close: 0.0,
                                                volume: 0.0,
                                                close_time: 0,
                                                number_of_trades: 0,
                                                taker_buy_base_asset_volume: 0.0,
                                            };
                                            last_kline_period = 0;
                                            last_volume_period = 0;
                                        }
                                    }
                                }
                            }
                            Ok(volume_data) = volume_receiver.recv() => {
                                ws_client_for_data.update_time().await;
                                let current_time = ws_client_for_data.get_current_time().await;
                                
                                let current_period = volume_data.period_id;
                                let mut current = data_clone.current_data.write().await;
                                if current_period >= last_volume_period {
                                    Self::process_volume_data(&volume_data, &mut current, current_period, last_volume_period).await;
                                    last_volume_period = current_period;
                                    
                                    if current.close > 0.0 && last_kline_period == current_period {
                                        if Self::send_data(
                                            &current,
                                            &instrument_id_clone,
                                            &callback_clone,
                                            current_time,
                                            &data_clone.sending_lock,
                                            &data_clone.current_period,
                                            current_period,
                                        ).await {
                                            // 重置数据
                                            *current = ResampleKlineData {
                                                instrument_id: instrument_id_clone.clone(),
                                                open_time: 0,
                                                open: 0.0,
                                                high: 0.0,
                                                low: f64::MAX,
                                                close: 0.0,
                                                volume: 0.0,
                                                close_time: 0,
                                                number_of_trades: 0,
                                                taker_buy_base_asset_volume: 0.0,
                                            };
                                            last_kline_period = 0;
                                            last_volume_period = 0;
                                        }
                                    }
                                }
                            }
                            else => {
                                error!("Error receiving data for {}", instrument_id_clone);
                                tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
                                continue;
                            }
                        }
                    }
                });
            });
        }

        Ok(())
    }
} 