#!/bin/bash

# voicevoxをバックグラウンドで起動
/usr/local/bin/voicevox_engine &

# Pythonプログラムを起動
python3 /app/main.py
