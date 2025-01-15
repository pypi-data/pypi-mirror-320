import time

from rnode import init_resample_kline_node


def total_volume_callback(data: str):
    """处理交易量数据的回调"""
    print(f"\nReceived total volume data: {data}")


def mid_price_callback(data: str):
    """处理中间价数据的回调"""
    print(f"\nReceived mid price data: {data}")


def kline_callback(data: str):
    """处理K线数据的回调"""
    print(f"\nReceived kline data: {data}")


def resample_kline_callback(data: str):
    """处理K线数据的回调"""
    print(f"\nReceived resample kline data: {data}")


def main():
    try:
        # 初始化K线节点
        # init_total_volume_node(
        #     "ws://43.207.106.154:5002/ws/dms",
        #     [
        #         "EXCHANGE_BINANCE.BTC-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
        #         "EXCHANGE_BINANCE.ETH-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
        #         "EXCHANGE_BINANCE.ADA-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
        #         "EXCHANGE_BINANCE.XRP-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
        #         "EXCHANGE_BINANCE.LINK-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
        #         "EXCHANGE_BINANCE.SOL-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
        #     ],
        #     "10s",
        #     kline_callback,
        # )

        init_resample_kline_node(
            "ws://43.207.106.154:5002/ws/dms",
            [
                "EXCHANGE_BINANCE.BTC-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
                "EXCHANGE_BINANCE.ETH-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
                "EXCHANGE_BINANCE.ADA-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
                "EXCHANGE_BINANCE.XRP-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
                "EXCHANGE_BINANCE.LINK-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
                "EXCHANGE_BINANCE.SOL-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
            ],
            "10s",
            resample_kline_callback,
        )

        print("Services started. Waiting for data...")

        while True:
            time.sleep(1)
            print(".", end="", flush=True)

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
