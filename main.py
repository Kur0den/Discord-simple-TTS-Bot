# 必要なモジュールをインポート
# Discord関係
import discord
from discord import app_commands
from discord.ext import commands

# ファイル操作関係
import os
import shutil

# json関係
import json

# gTTS関係
from gtts import gTTS


# configを読み込み
config = json.load(open("config.json"))

# インスタンス定義
bot = commands.Bot(
    command_prefix=config["prefix"],
    case_insensitive=True,
    activity=discord.Activity(type=discord.ActivityType.listening, name="!join"),
    intents=discord.Intents.all(),
)


@bot.event
async def on_ready():
    # 起動時に実行する処理

    # 設定ファイルから読み上げ用のフォルダを取得
    bot.tts_folder = config["tts_folder"]

    try:
        shutil.rmtree(bot.tts_folder)
    except FileNotFoundError:
        pass
    finally:
        os.mkdir(bot.tts_folder)
    print("Bot is ready.")


# @app_commands.command(name="VCJoin", description="VCに参加して読み上げを開始します")
# @app_commands.guild_only(guild_ids=[config["guild_id"]])
# async def VC_join(interaction: discord.Interaction):
#     await interaction.response.send_message("VCに参加します")


bot.run(config["token"])
