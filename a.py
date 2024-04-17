from obswebsocket import obsws, requests

host = "localhost"
port = 4444
password = "your_password"

ws = obsws(host, port, password)
ws.connect()

# ストリーミングの開始
ws.call(requests.StartStreaming())

# ここで何らかの処理を行う（例: sleepで一定時間待つなど）
import time

time.sleep(10)  # ストリーミングを10秒間継続

# ストリーミングの停止
ws.call(requests.StopStreaming())

ws.disconnect()
