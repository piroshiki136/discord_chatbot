#!/bin/bash

# voicevoxをバックグラウンドで起動
python3 run.py --use_gpu --voicelib_dir /opt/voicevox_core/ --runtime_dir /opt/onnxruntime/lib --host 0.0.0.0 &

# 少し待機してからmain.pyを実行
sleep 5

# Pythonプログラムを起動
python3 /scr/app/main.py
