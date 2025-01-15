import json
import signal
import time

from rnode import PyWsClient


def signal_handler(signum, frame):
    raise KeyboardInterrupt()

def ws_callback(message: str):
    """处理 WebSocket 消息的回调"""
    print("\nReceived WebSocket message:")
    try:
        data = json.loads(message)
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError:
        print(f"Raw message: {message}")

def main():
    signal.signal(signal.SIGALRM, signal_handler)
    client = None
    
    try:
        client = PyWsClient("ws://43.207.106.154:5002/ws/dms")
        
        # 创建一个接收器并保持引用
        def ws_callback(message: str):
            try:
                data = json.loads(message)
                print("\nReceived message:")
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print(f"\nRaw message: {message}")
        
        client.connect(ws_callback)
        print("WebSocket client started. Waiting for messages...")
        time.sleep(1)
        
        messages = [
            {
                "event": "sub",
                "topic": "trade.EXCHANGE_BINANCE.BTC-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED"
            },
            {
                "event": "sub",
                "topic": "bbo.EXCHANGE_BINANCE.BTC-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED"
            }
        ]
        
        for msg in messages:
            msg_str = json.dumps(msg)
            print(f"\nSending message: {msg_str}")
            signal.alarm(5)
            try:
                client.send(msg_str)
                signal.alarm(0)
                print("Message sent successfully")
            except KeyboardInterrupt:
                print("Message send timeout")
            time.sleep(0.5)
        
        # 保持主循环运行，确保接收器不会被关闭
        while True:
            time.sleep(1)
            print(".", end="", flush=True)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client:
            try:
                client.close()
            except:
                pass

if __name__ == "__main__":
    main() 