from rnode import DataCallback, DataStatus, KlineData, NodeResponse, init_kline_node


def kline_callback(data: str) -> None:
    """处理K线数据的回调函数"""
    response = NodeResponse.from_json(data)
    if response.status == DataStatus.BASIC_VALID and isinstance(
        response.data, KlineData
    ):
        print(f"Received kline: Open={response.data.open}, Close={response.data.close}")


# 使用类型提示的函数
def init_node(callback: DataCallback) -> None:
    """初始化K线节点"""
    init_kline_node("ws://example.com", ["BTC-USDT"], "1m", callback)
