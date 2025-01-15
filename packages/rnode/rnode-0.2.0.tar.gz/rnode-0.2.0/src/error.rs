use std::fmt;

#[derive(Debug)]
pub enum MarketDataError {
    WebSocketError(String),
}

impl std::error::Error for MarketDataError {}

impl fmt::Display for MarketDataError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            MarketDataError::WebSocketError(msg) => write!(f, "WebSocket error: {}", msg),
        }
    }
}

pub type Result<T> = std::result::Result<T, MarketDataError>; 