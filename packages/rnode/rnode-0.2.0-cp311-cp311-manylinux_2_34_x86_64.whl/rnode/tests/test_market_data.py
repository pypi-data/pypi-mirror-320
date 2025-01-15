import json
import time
from dataclasses import dataclass
from typing import Optional

from rnode import init_market_data_service


@dataclass
class MarketData:
    """市场数据基类"""

    timestamp: int
    status: str


@dataclass
class TotalVolumeData(MarketData):
    exchange_time: int
    total_volume: float
    taker_buy_base_asset_volume: float
    number_of_trades: int


@dataclass
class MidPriceData(MarketData):
    exchange_time: int
    mid_prc: float


@dataclass
class SimpleKlineData(MarketData):
    open_time: int
    open: float
    high: float
    low: float
    close: float
    close_time: int


class MarketDataTester:
    def __init__(self):
        self.volume_data: Optional[TotalVolumeData] = None
        self.mid_price_data: Optional[MidPriceData] = None
        self.kline_data: Optional[SimpleKlineData] = None
        self.message_count = 0
        self.start_time = time.time()

    def callback(self, data_type: str, data: str):
        try:
            data_obj = json.loads(data)
            self.message_count += 1

            if data_type == "total_volume" and data_obj.get("data"):
                self._handle_volume_data(data_obj)
            elif data_type == "mid_price" and data_obj.get("data"):
                self._handle_mid_price_data(data_obj)
            elif data_type == "kline" and data_obj.get("data"):
                self._handle_kline_data(data_obj)

            # 每100条消息打印一次统计信息
            if self.message_count % 100 == 0:
                self._print_stats()

        except Exception as e:
            print(f"Error processing data: {e}")

    def _handle_volume_data(self, data_obj):
        d = data_obj["data"]
        self.volume_data = TotalVolumeData(
            timestamp=data_obj["timestamp"],
            status=data_obj["status"],
            exchange_time=d["exchange_time"],
            total_volume=d["total_volume"],
            taker_buy_base_asset_volume=d["taker_buy_base_asset_volume"],
            number_of_trades=d["number_of_trades"],
        )
        print(f"\nVolume Data: {self.volume_data}")

    def _handle_mid_price_data(self, data_obj):
        d = data_obj["data"]
        self.mid_price_data = MidPriceData(
            timestamp=data_obj["timestamp"],
            status=data_obj["status"],
            exchange_time=d["exchange_time"],
            mid_prc=d["mid_prc"],
        )
        print(f"\nMid Price Data: {self.mid_price_data}")

    def _handle_kline_data(self, data_obj):
        d = data_obj["data"]
        self.kline_data = SimpleKlineData(
            timestamp=data_obj["timestamp"],
            status=data_obj["status"],
            open_time=d["open_time"],
            open=d["open"],
            high=d["high"],
            low=d["low"],
            close=d["close"],
            close_time=d["close_time"],
        )
        print(f"\nKline Data: {self.kline_data}")

    def _print_stats(self):
        elapsed = time.time() - self.start_time
        msg_rate = self.message_count / elapsed
        print(f"\nStats after {self.message_count} messages:")
        print(f"Running time: {elapsed:.2f} seconds")
        print(f"Message rate: {msg_rate:.2f} messages/second")


def main():
    ws_url = "ws://43.207.106.154:5002/ws/dms"
    tester = MarketDataTester()

    try:
        print("Starting market data service...")
        init_market_data_service(ws_url, tester.callback)

        print("Service running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
