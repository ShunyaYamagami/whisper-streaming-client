import json
import subprocess
from dataclasses import dataclass


@dataclass
class ASRResult:
    start: float
    end: float
    text: str


VIDEO_PATH = "wavs/full.mp4"
AUDIO_PATH = "wavs/full.wav"
PORT = 15504
OUT_TEXT_PATH = "realtime_subtitles.txt"

# STREAM_COMMAND = f"ffmpeg -re -i {VIDEO_PATH} -c copy -f flv rtmp://localhost/live/stream"
STREAM_COMMAND = (
    f"ffmpeg -re -i {VIDEO_PATH} -vf"
    + f' "drawtext=textfile={OUT_TEXT_PATH}:reload=1:x=10:y=H-th-10:fontsize=64:fontcolor=white:box=1:boxcolor=black@0.5"'
    + " -c:a copy -f flv rtmp://localhost/live/stream"
)
# コマンドをバックグラウンドで実行
streaming_process = subprocess.Popen(STREAM_COMMAND, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print("*" * 100)
print("start streaming")
print(STREAM_COMMAND)
print("*" * 100)

# soxコマンドを使用して音声データを変換し、サーバに送信
COMMAND = f"sox {AUDIO_PATH} -e signed -b 16 -c 1 -r 16000 -t raw - | pv -L 32000 | nc 0.tcp.jp.ngrok.io {PORT}"
print(COMMAND)
print()

process = subprocess.Popen(COMMAND, shell=True, stdout=subprocess.PIPE)

while True:
    # TODO: 標準出力をキャプチャして結果を取得すると意図しないバグが発生する。
    output = process.stdout.readline()
    # output, _ = process.communicate()
    if not output:
        break
    output = output.decode()
    output = output.replace("\n", "")
    output = output.rstrip().lstrip()
    print(rf"{output}")
    print(len(output))
    if not output:
        continue
    try:
        decoded_json = json.loads(output)
    except json.JSONDecodeError:
        print(f"Invalid JSON format: {output}")
        continue
    # asr_results = [ASRResult(**d) for d in decoded_json]
    # text = "\n".join([a.text for a in asr_results])
    # print(text)
    # f.write(text)
    # f.flush()
    with open(OUT_TEXT_PATH, "w") as f:
        f.write(output)
        f.flush()
