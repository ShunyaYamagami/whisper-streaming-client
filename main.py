import json
import socket
import subprocess
import tempfile
import threading
import wave

import pyaudio
from pydub import AudioSegment

AUDIO_FILE = "wavs/converted.wav"
SERVER_HOST = "0.tcp.jp.ngrok.io"
SERVER_PORT = 16270

FORMAT = pyaudio.paInt16  # 16ビットフォーマット
CHANNELS = 1
SAMPLING_RATE = 16000
BIT_RATE = "16k"
CHUNK_SIZE = 4096  # バッファサイズ
BIT_WIDTH = 16


def listen_for_responses(sock: socket.socket):
    """サーバーからのレスポンスをリスニングする"""
    while True:
        response = sock.recv(CHUNK_SIZE)
        if not response:
            break  # サーバーからのデータがなければ終了
        response_data = json.loads(str(response.decode("utf-8").replace("'", '"')))
        print(json.dumps(response_data, indent=4, ensure_ascii=False))
        print("*" * 100)


def send_server_sox(sock: socket.socket):
    # soxコマンドをsubprocessで実行し、標準出力をパイプで直接読み込む
    sox_command = f"sox {AUDIO_FILE} -e signed -b 16 -c 1 -r {SAMPLING_RATE} -t raw - | pv -L 32000"
    with subprocess.Popen(sox_command, stdout=subprocess.PIPE, shell=True) as proc:
        while True:
            data = proc.stdout.read(CHUNK_SIZE)
            if not data:
                break
            sock.sendall(data)


def send_server_mic(sock: socket.socket):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=SAMPLING_RATE, input=True, frames_per_buffer=CHUNK_SIZE)
    try:
        while True:
            data = stream.read(CHUNK_SIZE)
            if not data:
                break
            sock.sendall(data)
    except KeyboardInterrupt:
        print("Streaming stopped")

    stream.stop_stream()
    stream.close()
    audio.terminate()


def send_server_audiofile(sock: socket.socket):
    audio: AudioSegment
    audio = AudioSegment.from_wav(AUDIO_FILE)
    audio = audio.set_channels(CHANNELS)
    audio = audio.set_frame_rate(SAMPLING_RATE)
    audio = audio.set_sample_width(BIT_WIDTH)

    with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_file:
        audio.export(temp_file.name, format="wav", bitrate=BIT_RATE)

        with wave.open(temp_file.name, "rb") as wf:
            data = wf.readframes(CHUNK_SIZE)
            try:
                while True:
                    data = wf.readframes(CHUNK_SIZE)
                    if not data:
                        break
                    sock.sendall(data)
            except KeyboardInterrupt:
                print("Streaming stopped")


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_HOST, SERVER_PORT))

        listener_thread = threading.Thread(target=listen_for_responses, args=(sock,))
        listener_thread.start()

        # send_server_sox(sock)
        # send_server_mic(sock)
        send_server_audiofile(sock)

        listener_thread.join()
