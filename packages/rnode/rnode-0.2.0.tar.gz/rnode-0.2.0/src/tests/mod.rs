#[cfg(test)]
mod tests {
    use super::*;
    use crate::nodes::*;
    use crate::types::*;
    use tokio::runtime::Runtime;
    
    #[test]
    fn test_parse_freq() {
        assert_eq!(parse_freq("1s").unwrap().num_seconds(), 1);
        assert_eq!(parse_freq("5m").unwrap().num_minutes(), 5);
        assert_eq!(parse_freq("1h").unwrap().num_hours(), 1);
        assert_eq!(parse_freq("1D").unwrap().num_days(), 1);
        assert!(parse_freq("invalid").is_none());
    }

    #[test]
    fn test_total_volume_node() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let node = TotalVolumeNode::new("1s".to_string(), "BTCUSDT".to_string());
            
            // 测试数据
            let test_data = r#"{
                "topic": "trade.BTCUSDT",
                "tt": 1635000000000000,
                "body": {
                    "t": 123,
                    "p": "50000.0",
                    "q": "1.5",
                    "d": "buy"
                }
            }"#;
            
            let response = node.process_data(test_data).await.unwrap();
            assert!(response.data.is_some());
            
            if let Some(data) = response.data {
                assert_eq!(data.total_volume, 1.5);
                assert_eq!(data.taker_buy_base_asset_volume, 1.5);
                assert_eq!(data.number_of_trades, 1);
            }
        });
    }

    #[test]
    fn test_mid_price_node() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let node = MidPriceNode::new("1s".to_string(), "BTCUSDT".to_string());
            
            // 测试数据
            let test_data = r#"{
                "topic": "bbo.BTCUSDT",
                "tt": 1635000000000000,
                "body": [
                    ["50100.0", "1.0", "1.0"],
                    ["50000.0", "1.0", "1.0"]
                ]
            }"#;
            
            let response = node.process_data(test_data).await.unwrap();
            assert!(response.data.is_some());
            
            if let Some(data) = response.data {
                assert_eq!(data.mid_prc, 50050.0);
            }
        });
    }
} 