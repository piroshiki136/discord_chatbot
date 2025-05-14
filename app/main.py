import io
import os
from typing import Optional

import aiohttp
import discord
import google.generativeai as genai
from discord import Embed, FFmpegPCMAudio, app_commands
from discord.ext import commands
from dotenv import load_dotenv

# from server import server_thread

# ===============================
# 設定の読み込み
# ===============================

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VOICEVOX_API_KEY = os.getenv("VOICEVOX_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ===============================
# Discord Bot の設定
# ===============================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ===============================
# プロンプトテンプレート読み込み関数
# ===============================


def load_prompt_template(filepath: str) -> str:
    """
    指定されたファイルからプロンプトテンプレートを読み込む関数。
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "（テンプレートが読み込めませんでした）"


# ===============================
# Geminiへの問い合わせ関数
# ===============================


def get_gemini_response(full_message: str) -> str:
    """
    Geminiにメッセージを送り、返答を受け取る関数。
    """
    try:
        # これでメッセージが混同されない
        chat_session = model.start_chat()
        response = chat_session.send_message(full_message)
        return response.text
    except Exception as e:
        return f"❌ エラーが発生しました: {str(e)}"


# ===============================
# 音声合成関数 (Web API使用)
# ===============================


async def synthesize(text: str, speaker: int = 8) -> Optional[bytes]:
    """
    su-shiki の VoiceVox API を使って音声合成し、音声バイナリを返す。
    """
    url = "https://api.su-shiki.com/v2/voicevox/audio/"
    params = {"text": text, "key": VOICEVOX_API_KEY, "speaker": speaker}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    print(f"音声生成に失敗しました: {resp.status}")
                    return None
                audio_data = await resp.read()
                return audio_data
    except Exception as e:
        print(f"音声生成中にエラーが発生しました: {e}")
        return None


# ===============================
# 音声を再生する関数
# ===============================


async def play_speech(vc: discord.VoiceClient, speech_data: bytes):
    """
    合成した音声をボイスチャットで再生する関数。
    """
    if vc.is_playing():
        vc.stop()

    # メモリ上に音声データを保持する
    audio_source = FFmpegPCMAudio(source=io.BytesIO(speech_data), pipe=True)
    vc.play(audio_source)


# ===============================
# ボイスチャットに参加するコマンド
# ===============================


async def join_voice_channel(interaction: discord.Interaction):
    """ボイスチャットに参加する処理"""
    channel = interaction.user.voice.channel if interaction.user.voice else None
    print(channel)
    if channel:
        vc = await channel.connect()
        await interaction.response.send_message(f"ボイスチャットに参加しました: {channel.name}")
        return vc
    else:
        await interaction.response.send_message(
            "ボイスチャットに接続しているチャネルがありません。"
        )
        return None


# ===============================
# ボイスチャットから抜けるコマンド
# ===============================


async def leave_voice_channel(interaction: discord.Interaction):
    """ボイスチャットから抜ける処理"""
    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if vc:
        await vc.disconnect()
        await interaction.response.send_message("ボイスチャットから抜けました。")
    else:
        await interaction.response.send_message("ボイスチャットに参加していません。")


# ===============================
# Bot 起動時の処理
# ===============================


@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ ログイン成功: {bot.user}")


# ===============================
# 会話するコマンド
# ===============================


@tree.command(name="chat", description="ツンデレ幼馴染と会話します")
@app_commands.describe(message="ツンデレ幼馴染へのメッセージ")
async def chat(interaction: discord.Interaction, message: str):
    await interaction.response.defer()

    # 会話履歴の取得
    chat_history = []
    async for message_history in interaction.channel.history(limit=5):
        text = message_history.content
        if message_history.embeds:
            embed_title = message_history.embeds[0].title
            embed_description = message_history.embeds[0].description
            text += f", {embed_title}: {embed_description}"
        chat_history.append(f"{message_history.author}: {text}")
        print(chat_history)
    chat_history.reverse()
    chat_history = "\n".join(chat_history)

    # テンプレートを読み込み、ユーザーメッセージと結合
    prompt = load_prompt_template("prompt.txt")
    full_message = f"直前の会話履歴{chat_history}\n\n{prompt}{message}"

    # Geminiに送信し、返答を取得
    response = get_gemini_response(full_message)

    # エラーの場合
    if response.startswith("❌"):
        await interaction.followup.send(response)
        return

    # Embed作成
    embed = Embed(title="ツンデレ幼馴染の返答", description=response, color=0x00FF00)
    # メッセージをEmbedで送信
    await interaction.followup.send(f"**メッセージ: **{message}", embed=embed)

    # ボイスチャットにBotがいる場合、返答を読み上げ
    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if vc and vc.is_connected():
        speech_data = await synthesize(response)
        if speech_data:
            await play_speech(vc, speech_data)
        else:
            await interaction.followup.send(
                "音声合成に失敗しました。APIのポイントが不足している可能性があります。"
            )
            vc.play(discord.FFmpegPCMAudio("error.wav"))


# ===============================
# ボイスチャットコマンド
# ===============================


@tree.command(name="join", description="ボイスチャットに参加します")
async def join(interaction: discord.Interaction):
    await join_voice_channel(interaction)


@tree.command(name="leave", description="ボイスチャットから抜けます")
async def leave(interaction: discord.Interaction):
    await leave_voice_channel(interaction)


# ===============================
# サーバー起動
# ===============================
# server_thread()


# ===============================
# Bot の実行
# ===============================

bot.run(DISCORD_TOKEN)
