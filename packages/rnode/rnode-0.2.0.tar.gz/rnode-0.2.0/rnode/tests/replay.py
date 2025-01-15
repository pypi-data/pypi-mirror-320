import time
from datetime import datetime

import rnode


def callback(msg):
    print(f"Received: {msg}")


def main():
    # 设置回放参数
    ws_url = "ws://172.18.49.26:8081/ws/replay"  # replay websocket URL
    instrument_id = "EXCHANGE_BINANCE.BTC-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED"
    freq = "10s"  # 1分钟 K线

    # 设置时间范围
    start_time = int(
        datetime(2022, 9, 1, 0, 0, 0).timestamp() * 1000
    )  # 2022-09-01 00:00:00
    end_time = int(
        datetime(2022, 9, 2, 0, 0, 0).timestamp() * 1000
    )  # 2022-09-02 00:00:00

    # 回放配置
    speed_multiplier = 1.0  # 回放速度倍数
    replay_window = 0  # 回放窗口大小(秒)
    x_cur_time = start_time  # 初始时间戳

    try:
        # 初始化并启动回放节点
        rnode.init_resample_kline_node_replay(
            ws_url,
            [instrument_id],
            freq,
            callback,
            start_time,
            end_time,
            speed_multiplier,
            replay_window,
            x_cur_time,
        )

        print(
            f"Started replay for {instrument_id} from {datetime.fromtimestamp(start_time / 1000)}"
        )

        # 保持程序运行直到回放结束
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping replay...")
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
