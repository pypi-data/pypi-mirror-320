"""
RNode - A high-performance market data service

This package provides Python bindings for the Rust-based market data service,
offering efficient processing of real-time market data.

Available functions:
    init_total_volume_node: Initialize a total volume calculation node
    init_mid_price_node: Initialize a mid-price calculation node
    init_kline_node: Initialize a Kline (candlestick) calculation node
"""

from .interface import (
    NodeInterface,
    init_kline_node,
    init_mid_price_node,
    init_resample_kline_node,
    init_resample_kline_node_replay,
    init_total_volume_node,
)
from .rnode import PyWsClient
from .types import (
    DataCallback,
    DataStatus,
    KlineData,
    MidPriceData,
    NodeResponse,
    TotalVolumeData,
)

__version__ = "0.1.7"
__author__ = "stark <ywiscat@gmail.com>"

__all__ = [
    # Interfaces
    "init_total_volume_node",
    "init_mid_price_node",
    "init_kline_node",
    "init_resample_kline_node",
    "init_resample_kline_node_replay",
    "NodeInterface",
    # Classes
    "PyWsClient",
    # Types
    "DataCallback",
    "DataStatus",
    "TotalVolumeData",
    "MidPriceData",
    "KlineData",
    "NodeResponse",
]
