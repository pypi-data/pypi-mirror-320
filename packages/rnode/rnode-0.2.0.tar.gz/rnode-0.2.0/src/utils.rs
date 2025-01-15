use std::sync::Arc;
use crate::ws_client::WsClient;

pub struct IntervalManager {
    duration_ms: i64,    // 周期长度（毫秒）
    current_index: i64,  // 当前周期索引
}

impl IntervalManager {
    pub fn new(freq: String, ws_client: Arc<WsClient>) -> Option<Self> {
        let duration_ms = parse_duration(&freq)?;
        let current_time = tokio::task::block_in_place(|| {
            tokio::runtime::Handle::current().block_on(async {
                ws_client.get_current_time().await
            })
        });
        let current_index = current_time / duration_ms;
        
        Some(Self {
            duration_ms,
            current_index,
        })
    }

    pub fn get_current_interval(&self) -> (i64, i64) {
        let start = self.current_index * self.duration_ms;
        let end = start + self.duration_ms;
        (start, end)
    }

    pub fn advance(&mut self) {
        self.current_index += 1;
    }

    pub fn should_advance(&self, timestamp: i64) -> bool {
        let (_, current_end) = self.get_current_interval();
        timestamp >= current_end
    }

    pub fn get_current_period(&self) -> i64 {
        self.current_index
    }

    pub fn get_period_id(&self, timestamp: i64) -> i64 {
        timestamp / self.duration_ms
    }
}

pub fn parse_duration(freq: &str) -> Option<i64> {
    let len = freq.len();
    if len < 2 {
        return None;
    }

    let (num_str, unit) = freq.split_at(len - 1);
    let num: i64 = num_str.parse().ok()?;

    match unit {
        "s" => Some(num * 1000),           // 秒转毫秒
        "m" => Some(num * 60 * 1000),      // 分钟转毫秒
        "h" => Some(num * 3600 * 1000),    // 小时转毫秒
        "d" => Some(num * 86400 * 1000),   // 天转毫秒
        _ => None,
    }
}
