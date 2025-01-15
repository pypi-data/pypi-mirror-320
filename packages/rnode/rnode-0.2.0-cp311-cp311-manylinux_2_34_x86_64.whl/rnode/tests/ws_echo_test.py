import time

from rnode import init_market_data_service


def market_data_callback(data_type: str, data: str):
    """回调函数，用于处理来自 Rust 的数据"""
    print(f"\nCallback triggered with type: {data_type}")
    print(f"Raw data: {data}")


def main():
    try:
        # 使用 echo.websocket.org 服务器
        init_market_data_service(
            "wss://echo.websocket.org",  # 使用安全的 WebSocket 连接
            "test_instrument",  # 简单的测试标识符
            "10s",
            "10s",
            market_data_callback,
        )

        print("Service started. Waiting for data...")

        # 保持程序运行
        while True:
            time.sleep(1)
            print(".", end="", flush=True)

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
