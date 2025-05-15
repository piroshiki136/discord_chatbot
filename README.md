# 💬 ツンデレ幼馴染と会話できる Discord Bot

**ツンデレな幼馴染キャラと会話できる Discord Bot** です。  
Google Gemini API を活用し、VC（ボイスチャット）にいる場合は **音声でも返答**してくれます。  

---

## ✨ 主な機能

- `/chat`: テキストチャットで会話。VCにBotがいると**音声でも返答**します。
- `/join`: VCにBotを参加させます。
- `/leave`: VCからBotを退出させます。

---

## 🛠 使用技術

| 項目       | 内容                         |
|------------|------------------------------|
| 言語       | Python 3.12                  |
| Discord API | [discord.py](https://github.com/Rapptz/discord.py) |
| AI連携     | Google Gemini API            |
| 音声合成   | 非公式 VoiceVox API          |

---

## 🚀 セットアップ方法
-mainブランチ voicevoxをローカルで動かす(調整中)
-slow-voicevox-api 無制限低速voicevoxapiを使用
-fast-voicevox-api 制限高速voicevoxapiを使用

```bash
git clone https://github.com/yourname/discord-studybot.git
cd discord-studybot
pip install -r requirements.txt
```
.envファイルを作成し、以下の情報を入力
DISCORD_TOKEN=xxx
GEMINI_API_KEY=xxx
VOICEVOX_API_KEY=xxx

常時起動する場合は任意のサーバーにデプロイ

## 今後のアップデート予定
- /helloなどの定型音声コマンドの追加
