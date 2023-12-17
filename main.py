# 必要なモジュールをインポート
# Discord関係
import discord
from discord import app_commands
from discord.ext import commands

# asyncio関係
import asyncio

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


# ping用のcogクラス
class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("pong")


# TTS用のcogクラス
class Tts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None

    @app_commands.command(name="connect", description="VCに接続します")
    @app_commands.guilds(config["guild_id"])
    @app_commands.guild_only()
    async def connect(self, interaction: discord.Interaction):
        # 呼び出されたチャンネルがVCチャンネルかどうかを判定
        if interaction.channel.type is not discord.ChannelType.voice:
            # VCチャンネルでない場合はエラーを返す
            await interaction.response.send_message(
                "VCチャンネルでこのコマンドを実行してください", ephemeral=True
            )
        else:
            # VCチャンネルの場合で、botがVCに接続していない場合は接続する
            if self.voice_client is None:
                self.voice_client = await interaction.channel.connect()
                await interaction.response.send_message("接続しました")
            else:
                # botがVCに接続している場合はエラーを返す
                await interaction.response.send_message("すでにVCに接続しています", ephemeral=True)

    @app_commands.command(name="disconnect", description="VCから切断します")
    @app_commands.guilds(config["guild_id"])
    @app_commands.guild_only()
    async def disconnect(self, interaction: discord.Interaction):
        # 呼び出されたチャンネルがVCチャンネルかどうかを判定
        if interaction.channel.type is not discord.ChannelType.voice:
            # VCチャンネルでない場合はエラーを返す
            await interaction.response.send_message(
                "VCチャンネルでこのコマンドを実行してください", ephemeral=True
            )
            return
        else:
            # VCチャンネルの場合で、botがVCに接続している場合は切断する
            if self.voice_client is not None:
                # botが呼び出されたVCに接続している場合は切断する
                if self.voice_client.channel is interaction.channel:
                    await self.voice_client.disconnect()
                    self.voice_client = None
                    await interaction.response.send_message("切断しました")
                else:
                    # botが呼び出されたVCに接続していない場合はエラーを返す
                    await interaction.response.send_message(
                        "接続しているVCでコマンドを実行してください", ephemeral=True
                    )
            else:
                # botがVCに接続していない場合はエラーを返す
                await interaction.response.send_message("VCに接続されていません", ephemeral=True)


@bot.event
async def on_ready():
    # 起動時に実行する処理

    # 読み上げ用の音声ファイルを保存するフォルダを作成
    try:
        shutil.rmtree(config["tts_folder"])
    except FileNotFoundError:
        pass
    finally:
        os.mkdir(config["tts_folder"])

    # cogをロード
    await bot.add_cog(Ping(bot))
    await bot.add_cog(Tts(bot))

    # jishakuをロード
    await bot.load_extension("jishaku")
    print("Bot is ready.")


@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(
        title="Error",
        description=error,
        color=discord.Color.red(),
        timestamp=ctx.message.created_at,
    )
    await ctx.send(embed=embed)


bot.run(config["token"])
