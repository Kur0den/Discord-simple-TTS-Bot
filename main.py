# 必要なモジュールをインポート
# Discord関係
import discord
from discord import app_commands
from discord.ext import commands

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
    print("Bot is ready.")


@app_commands.command(name="VCJoin", description="VCに参加して読み上げを開始します")
@app_commands.guild_only(guild_ids=[config["guild_id"]])
async def VC_join(interaction: discord.Interaction):
    await interaction.response.send_message("VCに参加します")
