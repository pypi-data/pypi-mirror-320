use async_trait::async_trait;

#[async_trait]
pub trait DataNode {
    fn get_freq(&self) -> &str;
    fn get_instrument_id(&self) -> &str;
    fn reset(&self);
} 