# ffmpegを使ったやり方
## RTMPサーバー構築 
動画ファイルをストリーミング配信するために、
rtmpサーバをnginxで立て、
ffmpegで配信する。

third-partyのイメージを使ってdockerでnginxのrtmpサーバを立てるのが最も手っ取り早い.
(`tiangolo/nginx-rtmp`)
https://hub.docker.com/r/tiangolo/nginx-rtmp/

```
ffmpeg -re -i data/120.mp4 -c:v libx264 -c:a aac -strict -2 -f flv rtmp://localhost/live/stream
```
`-re`: リアルタイム速度で読み込み

OBSで配信しても良いだろうが、obs-websocketを使って実装すると、ややこしいので簡易的にffmpegで実装.

## テキストのリアルタイム重畳
文字起こし結果をテキストファイルに保存する。
先述のコマンドを以下のようにすることで、テキストをオーバーレイすることができる。
```
ffmpeg -re -i data/120.mp4 -vf "drawtext=textfile=realtime_subtitles.txt:reload=1:x=10:y=H-th-10:fontsize=64:fontcolor=white:box=1:boxcolor=black@0.5" -c:a copy -f flv rtmp://localhost/live/stream
```
