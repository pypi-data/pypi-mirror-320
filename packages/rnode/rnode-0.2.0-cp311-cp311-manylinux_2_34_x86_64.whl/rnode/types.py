import json
from dataclasses import dataclass
from typing import Callable, Optional

# 回调函数类型
DataCallback = Callable[[str], None]

# 数据状态枚举
class DataStatus:
    """数据状态枚举

    Attributes:
        BASIC_VALID: 数据有效且来自完整的时间周期
        INCOMPLETE: 数据有效但不是完整的时间周期（例如刚启动时的第一个周期）
        EMPTY: 没有数据
        INVALID: 数据无效
        ERROR: 处理过程中出现错误
        ONEWAY_QUOTE: 单边报价（只有买方或卖方）
        NON_MONO: 时间戳不单调
    """
    BASIC_VALID = "BASIC_VALID"
    INCOMPLETE = "INCOMPLETE"
    EMPTY = "EMPTY"
    INVALID = "INVALID"
    ERROR = "ERROR"
    ONEWAY_QUOTE = "ONEWAY_QUOTE"
    NON_MONO = "NON_MONO"

@dataclass
class TotalVolumeData:
    exchange_time: int
    total_volume: float
    taker_buy_volume: float
    number_of_trades: int

@dataclass
class MidPriceData:
    exchange_time: int
    mid_price: float

@dataclass
class KlineData:
    open_time: int
    open: float
    high: float
    low: float
    close: float
    close_time: int

@dataclass
class ResampleKlineData:
    instrument_id: str
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: int
    number_of_trades: int
    taker_buy_base_asset_volume: float

@dataclass
class NodeResponse:
    type: str
    instrument_id: str
    data: Optional[TotalVolumeData | MidPriceData | KlineData | ResampleKlineData]
    status: str
    timestamp: int

    @classmethod
    def from_json(cls, json_str: str) -> 'NodeResponse':
        data = json.loads(json_str)
        return cls(
            type=data["type"],
            instrument_id=data["instrument_id"],
            data=cls._parse_data(data),
            status=data["status"],
            timestamp=data["timestamp"]
        )

    @staticmethod
    def _parse_data(data: dict) -> Optional[TotalVolumeData | MidPriceData | KlineData | ResampleKlineData]:
        if data.get("data") is None:
            return None

        data_type = data["type"]
        data_content = data["data"]

        if data_type == "total_volume":
            return TotalVolumeData(
                exchange_time=data_content["exchange_time"],
                total_volume=data_content["total_volume"],
                taker_buy_volume=data_content["taker_buy_volume"],
                number_of_trades=data_content["number_of_trades"]
            )
        elif data_type == "mid_price":
            return MidPriceData(
                exchange_time=data_content["exchange_time"],
                mid_price=data_content["mid_price"]
            )
        elif data_type == "kline":
            return KlineData(
                open_time=data_content["open_time"],
                open=data_content["open"],
                high=data_content["high"],
                low=data_content["low"],
                close=data_content["close"],
                close_time=data_content["close_time"]
            )
        elif data_type == "resample_kline":
            return ResampleKlineData(
                instrument_id=data_content["instrument_id"],
                open_time=data_content["open_time"],
                open=data_content["open"],
                high=data_content["high"],
                low=data_content["low"],
                close=data_content["close"],
                volume=data_content["volume"],
                close_time=data_content["close_time"],
                number_of_trades=data_content["number_of_trades"],
                taker_buy_base_asset_volume=data_content["taker_buy_base_asset_volume"]
            )
        return None 