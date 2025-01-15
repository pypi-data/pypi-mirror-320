use std::sync::Arc;
use tokio::sync::RwLock;
use std::time::SystemTime;

pub struct MasterClock {
    start_time: i64,  // 回放开始时间
    speed_multiplier: f64,  // 速度倍数
    base_time: i64,   // 基准时间（真实时间）
    current_time: Arc<RwLock<i64>>,  // 当前模拟时间
}

impl MasterClock {
    pub fn new(start_time: i64, speed_multiplier: f64) -> Self {
        let current_time = Arc::new(RwLock::new(start_time));
        let base_time = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_millis() as i64;

        Self {
            start_time,
            speed_multiplier,
            base_time,
            current_time,
        }
    }

    pub async fn get_current_time(&self) -> i64 {
        *self.current_time.read().await
    }

    pub async fn update_time(&self) {
        let real_elapsed = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_millis() as i64 - self.base_time;
            
        let simulated_elapsed = (real_elapsed as f64 * self.speed_multiplier) as i64;
        let new_time = self.start_time + simulated_elapsed;
        
        *self.current_time.write().await = new_time;
    }
}

#[derive(Debug, Clone)]
pub struct ReplayConfig {
    pub start_time: i64,      // 开始时间（毫秒）
    pub end_time: i64,        // 结束时间（毫秒）
    pub speed_multiplier: f64, // 速度倍数
    pub replay_window: i64,    // 推送窗口（秒）
    pub x_cur_time: i64,      // 当前时间戳
}

impl ReplayConfig {
    pub fn new(
        start_time: i64,
        end_time: i64,
        speed_multiplier: f64,
        replay_window: i64,
        x_cur_time: i64,
    ) -> Self {
        Self {
            start_time,
            end_time,
            speed_multiplier,
            replay_window,
            x_cur_time,
        }
    }

    pub fn to_subscription_params(&self) -> serde_json::Value {
        serde_json::json!({
            "start_time": self.start_time,
            "end_time": self.end_time,
            "speed_multiplier": self.speed_multiplier,
            "replay_window": self.replay_window,
            "x-cur-time": self.x_cur_time,
        })
    }
} 