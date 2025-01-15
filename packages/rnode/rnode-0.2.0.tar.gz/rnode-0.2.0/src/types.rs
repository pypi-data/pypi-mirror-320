use serde::{Deserialize, Serialize};
use std::fmt;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DataStatus {
    BasicValid,
    Empty,
    Incomplete,
    Invalid,
    NonMono,
    OnewayQuote,
    CrossPrice,
    InvalidQty,
    Error(String),
}

impl fmt::Display for DataStatus {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            DataStatus::BasicValid => write!(f, "BASIC_VALID"),
            DataStatus::Empty => write!(f, "EMPTY"),
            DataStatus::Incomplete => write!(f, "INCOMPLETE"),
            DataStatus::Invalid => write!(f, "INVALID"),
            DataStatus::Error(e) => write!(f, "ERROR: {}", e),
            DataStatus::NonMono => write!(f, "NON_MONO"),
            DataStatus::OnewayQuote => write!(f, "ONEWAY_QUOTE"),
            DataStatus::CrossPrice => write!(f, "CROSS_PRICE"),
            DataStatus::InvalidQty => write!(f, "INVALID_QTY"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NodeResponse<T> {
    pub data: Option<T>,
    pub status: DataStatus,
    pub timestamp: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct TotalVolumeData {
    pub exchange_time: i64,
    pub total_volume: f64,
    pub taker_buy_base_asset_volume: f64,
    pub number_of_trades: i64,
    pub period_id: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MidPriceData {
    pub exchange_time: i64,
    pub mid_prc: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimpleKlineData {
    pub open_time: i64,
    pub open: f64,
    pub high: f64,
    pub low: f64,
    pub close: f64,
    pub close_time: i64,
    pub interval_ms: i64,
    pub period_id: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DmsEventType {
    KLINE,
    PRICE,
    LOB,
    BBO,
    TRADE,
    LIQUIDATION,
}

impl fmt::Display for DmsEventType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            DmsEventType::KLINE => write!(f, "kline"),
            DmsEventType::PRICE => write!(f, "price"),
            DmsEventType::LOB => write!(f, "lob"),
            DmsEventType::BBO => write!(f, "bbo"),
            DmsEventType::TRADE => write!(f, "trade"),
            DmsEventType::LIQUIDATION => write!(f, "liquidation"),
        }
    }
} 