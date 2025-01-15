import json
import time

from rnode import init_market_data_service


def market_data_callback(data_type: str, data: str):
    """回调函数，用于处理来自 Rust 的数据"""
    print(f"\nCallback triggered with type: {data_type}")
    try:
        data_obj = json.loads(data)
        print(f"Received {data_type} data:")
        print(json.dumps(data_obj, indent=2))
    except Exception as e:
        print(f"Error processing data: {e}")
        print(f"Raw data: {data}")


def main():
    try:
        init_market_data_service(
            "ws://43.207.106.154:5002/ws/dms",
            "EXCHANGE_BINANCE.BTC-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
            "10s",
            "10s",
            market_data_callback,
        )
        print("Service started. Waiting for data...")
        while True:
            time.sleep(1)
            print(".", end="", flush=True)  # 显示心跳

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
