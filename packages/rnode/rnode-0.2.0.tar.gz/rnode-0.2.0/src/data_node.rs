use crate::types::*;
use async_trait::async_trait;
use chrono::{DateTime, Duration, Utc};
use std::sync::Arc;
use parking_lot::RwLock;

#[async_trait]
pub trait DataNode<T> {
    async fn process_data(&self, data: &str) -> NodeResponse<T>;
    fn get_freq(&self) -> &str;
    fn get_instrument_id(&self) -> &str;
}

pub struct TotalVolumeNode {
    freq: String,
    instrument_id: String,
    last_exchange_time: Arc<RwLock<i64>>,
    current_data: Arc<RwLock<TotalVolumeData>>,
}

pub struct MidPriceNode {
    freq: String,
    instrument_id: String,
    last_exchange_time: Arc<RwLock<i64>>,
    current_data: Arc<RwLock<MidPriceData>>,
}

pub struct SimpleKlineNode {
    freq: String,
    instrument_id: String,
    last_exchange_time: Arc<RwLock<i64>>,
    current_data: Arc<RwLock<SimpleKlineData>>,
}

// 实现节点... 