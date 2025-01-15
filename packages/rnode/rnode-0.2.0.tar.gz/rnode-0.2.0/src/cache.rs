use parking_lot::RwLock;
use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, Instant};

#[allow(dead_code)]
pub struct CacheEntry<T> {
    data: T,
    timestamp: Instant,
}

#[allow(dead_code)]
pub struct Cache<T> {
    data: Arc<RwLock<HashMap<String, CacheEntry<T>>>>,
    ttl: Duration,
}

#[allow(dead_code)]
impl<T: Clone> Cache<T> {
    pub fn new(ttl: Duration) -> Self {
        Self {
            data: Arc::new(RwLock::new(HashMap::new())),
            ttl,
        }
    }

    pub fn get(&self, key: &str) -> Option<T> {
        let data = self.data.read();
        if let Some(entry) = data.get(key) {
            if entry.timestamp.elapsed() < self.ttl {
                return Some(entry.data.clone());
            }
        }
        None
    }

    pub fn set(&self, key: String, value: T) {
        let mut data = self.data.write();
        data.insert(key, CacheEntry {
            data: value,
            timestamp: Instant::now(),
        });
    }

    pub fn clear_expired(&self) {
        let mut data = self.data.write();
        data.retain(|_, entry| entry.timestamp.elapsed() < self.ttl);
    }
} 