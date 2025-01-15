from typing import List, Protocol, runtime_checkable

from .types import DataCallback


@runtime_checkable
class NodeInterface(Protocol):
    """Base interface for all market data nodes"""

    def start(self) -> None:
        """Start the node"""
        ...

    def stop(self) -> None:
        """Stop the node"""
        ...


def init_total_volume_node(
    ws_url: str,
    instrument_ids: List[str],
    freq: str,
    callback: DataCallback,
) -> None:
    """Initialize a total volume calculation node.

    Args:
        ws_url: WebSocket server URL
        instrument_ids: List of instrument IDs to subscribe to
        freq: Data frequency (e.g., "1s", "5m", "1h")
        callback: Callback function to handle the data

    Example:
        >>> def volume_callback(data: str) -> None:
        ...     response = NodeResponse.from_json(data)
        ...     if response.status == DataStatus.BASIC_VALID:
        ...         print(f"Volume: {response.data.total_volume}")
        >>> init_total_volume_node(
        ...     "ws://example.com",
        ...     ["BTC-USDT"],
        ...     "1m",
        ...     volume_callback
        ... )
    """
    from .rnode import init_total_volume_node as _init

    return _init(ws_url, instrument_ids, freq, callback)


def init_mid_price_node(
    ws_url: str,
    instrument_ids: List[str],
    freq: str,
    callback: DataCallback,
) -> None:
    """Initialize a mid-price calculation node.

    Args:
        ws_url: WebSocket server URL
        instrument_ids: List of instrument IDs to subscribe to
        freq: Data frequency (e.g., "1s", "5m", "1h")
        callback: Callback function to handle the data

    Example:
        >>> def price_callback(data: str) -> None:
        ...     response = NodeResponse.from_json(data)
        ...     if response.status == DataStatus.BASIC_VALID:
        ...         print(f"Mid Price: {response.data.mid_price}")
        >>> init_mid_price_node(
        ...     "ws://example.com",
        ...     ["BTC-USDT"],
        ...     "1m",
        ...     price_callback
        ... )
    """
    from .rnode import init_mid_price_node as _init

    return _init(ws_url, instrument_ids, freq, callback)


def init_kline_node(
    ws_url: str,
    instrument_ids: List[str],
    freq: str,
    callback: DataCallback,
) -> None:
    """Initialize a Kline (candlestick) calculation node.

    Args:
        ws_url: WebSocket server URL
        instrument_ids: List of instrument IDs to subscribe to
        freq: Data frequency (e.g., "1s", "5m", "1h")
        callback: Callback function to handle the data

    Example:
        >>> def kline_callback(data: str) -> None:
        ...     response = NodeResponse.from_json(data)
        ...     if response.status == DataStatus.BASIC_VALID:
        ...         print(f"Kline: O={response.data.open}, C={response.data.close}")
        >>> init_kline_node(
        ...     "ws://example.com",
        ...     ["BTC-USDT"],
        ...     "1m",
        ...     kline_callback
        ... )
    """
    from .rnode import init_kline_node as _init

    return _init(ws_url, instrument_ids, freq, callback)

def init_resample_kline_node(
    ws_url: str,
    instrument_ids: List[str],
    freq: str,
    callback: DataCallback,
) -> None:
    from .rnode import init_resample_kline_node as _init

    return _init(ws_url, instrument_ids, freq, callback)

def init_resample_kline_node_replay(
    ws_url: str,
    instrument_ids: List[str],
    freq: str,
    callback: DataCallback,
    start_time: int,
    end_time: int,
    speed_multiplier: float,
    replay_window: int,
    x_cur_time: int,
) -> None:
    """Initialize a resample kline node in replay mode.

    Args:
        ws_url: WebSocket server URL
        instrument_ids: List of instrument IDs to subscribe to
        freq: Data frequency (e.g., "1s", "5m", "1h")
        callback: Callback function to handle the data
        start_time: Start time in milliseconds
        end_time: End time in milliseconds
        speed_multiplier: Replay speed multiplier
        replay_window: Replay window in seconds
        x_cur_time: Current timestamp
    """
    from .rnode import init_resample_kline_node_replay as _init

    return _init(
        ws_url,
        instrument_ids,
        freq,
        callback,
        start_time,
        end_time,
        speed_multiplier,
        replay_window,
        x_cur_time,
    )