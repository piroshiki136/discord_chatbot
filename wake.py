import requests

url = "https://api.su-shiki.com/v2/voicevox/audio/"
params = {"text": "こんにちは、世界！", "key": "X2R9W6D9957_036", "speaker": 8}

response = requests.get(url, params=params)

if response.status_code == 200:
    with open("output.wav", "wb") as f:
        f.write(response.content)
    print("音声ファイルを保存しました。")
else:
    print(f"エラーが発生しました: {response.status_code}")
