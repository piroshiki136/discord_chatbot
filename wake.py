import os

import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv

# tokenの読み込み
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# botの設定
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 起動状態を追跡するフラグ
bot_online = False


# bot起動時の処理
@bot.event
async def on_ready():
    global bot_online
    print(f"Logged in as {bot.user}")
    bot_online = True  # Botがオンラインになったらフラグを立てる
    try:
        await bot.tree.sync()
    except Exception as e:
        print(f"Failed to sync: {e}")


@bot.tree.command(name="wake", description="幼馴染を起こす")
async def wake_command(interaction: discord.Interaction):
    global bot_online

    # Botがオンラインの場合
    if bot_online:
        await interaction.response.send_message("Botはすでにオンラインです！")
        return

    # Botがオフラインの場合のみ、Cloud RunのURLにリクエストを送る
    await interaction.response.defer()

    url = "https://sorry-maryanne-piroshiki421-0a2e5c0f.koyeb.app/"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            response_text = "ふ、ふーん。別にアンタが呼んだからって来たんじゃないんだからね！たまたま暇だっただけよ。…ま、少しだけなら相手してあげてもいいわよ。"
            # Embedの作成
            embed = discord.Embed(
                title="ツンデレ幼馴染の返答",
                description=response_text,
                color=0x00FF00,
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("ツンデレ幼馴染を起こすのに失敗しました。")
    except Exception as e:
        await interaction.followup.send(f"エラーが発生しました: {e}")


@bot.event
async def on_disconnect():
    global bot_online
    bot_online = False  # Botがオフラインになった場合、フラグを下げる


bot.run(DISCORD_TOKEN)
