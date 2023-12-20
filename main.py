# 必要なモジュールをインポート
# Discord関係
import discord
from discord import app_commands
from discord.ext import commands
from collections import deque

# 音声ファイルの名前用のuuid
from uuid import uuid4

# asyncio関係
import asyncio

# ファイル操作関係
import os
import shutil

# json関係
import json

# gTTS関係
from gtts import gTTS

# 正規表現関係
import re

# configを読み込み
config = json.load(open("config.json"))

# インスタンス定義
bot = commands.Bot(
    command_prefix=config["prefix"],
    case_insensitive=True,
    activity=discord.Activity(type=discord.ActivityType.listening, name="/connect"),
    intents=discord.Intents.all(),
)


# ping用のcogクラス
class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        pong = ":ping_pong:"
        embed = discord.Embed(
            title=f"{pong}Pong!", description=f"{round(self.bot.latency * 1000)}ms"
        )
        await ctx.send(embed=embed)


# TTS用のcogクラス
class Tts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.url_regex = r"https?://.*?( |$)"
        self.message_queue = deque([])

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
                    # 読み上げ用の音声ファイルを保存するフォルダを削除
                    try:
                        shutil.rmtree(config["tts_folder"])
                    except FileNotFoundError:
                        pass
                    finally:
                        os.mkdir(config["tts_folder"])
                else:
                    # botが呼び出されたVCに接続していない場合はエラーを返す
                    await interaction.response.send_message(
                        "接続しているVCでコマンドを実行してください", ephemeral=True
                    )
            else:
                # botがVCに接続していない場合はエラーを返す
                await interaction.response.send_message("VCに接続されていません", ephemeral=True)

    @app_commands.command(name="stop", description="読み上げを停止します")
    @app_commands.guilds(config["guild_id"])
    @app_commands.guild_only()
    async def stop(self, interaction: discord.Interaction):
        if interaction.channel is self.voice_client.channel:
            if self.voice_client.is_playing():
                self.voice_client.stop()
                self.message_queue.clear()
                await interaction.response.send_message("読み上げをストップしました")
            else:
                await interaction.response.send_message("読み上げ中ではありません", ephemeral=True)
        else:
            await interaction.response.send_message(
                "接続しているVCでコマンドを実行してください", ephemeral=True
            )

    # VC接続時に接続しているチャンネルに投稿されたメッセージを読み上げる処理
    @commands.Cog.listener()
    async def on_message(self, message):
        # botがVCに接続している場合のみ処理を行う
        if self.voice_client is not None:
            # 発言者がbotの場合は処理を行わない
            if message.author.bot:
                return
            if self.voice_client.channel is message.channel:
                # メッセージの内容を読み上げる
                i = 0
                for m in [
                    message async for message in message.channel.history(limit=2)
                ]:
                    if i == 0:
                        m1 = m.author.id
                    else:
                        m2 = m.author.id
                    i += 1
                usernick = message.author.display_name
                content = message.content[: config["read_limit"]]
                content = re.sub(self.url_regex, "URL ", content, flags=re.MULTILINE)
                if m1 == m2:
                    pass
                else:
                    content = usernick + ":" + content
                if content == "":
                    return
                await self.tts(content)

    # VC接続/切断時に接続しているVCでメッセージを読み上げる処理
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # botがVCに接続している場合のみ処理を行う
        if self.voice_client is not None:
            # 入退出以外を弾く
            if before.channel is not after.channel:
                # botが接続しているVCにメンバーが接続した場合はメンバーの名前を読み上げる
                if self.voice_client.channel is after.channel:
                    if member.bot:
                        return
                    content = f"{member.display_name}がVCに接続しました"
                    await self.tts(content)
                # botが接続しているVCからメンバーが切断した場合はメンバーの名前を読み上げる
                elif self.voice_client.channel is before.channel:
                    if member.bot:
                        return
                    content = f"{member.display_name}がVCから切断しました"
                await self.tts(content)

    # 読み上げ処理
    async def tts(self, content):
        if self.voice_client.is_playing():
            self.message_queue.append(content)
            while self.voice_client.is_playing():
                await asyncio.sleep(0.1)
            # 読み上げ停止時にバグるかもしれないのでtryで囲む
            content = self.message_queue.popleft()
        try:
            g_tts = gTTS(
                text=content,
                tld="jp",
                lang="ja",
            )
        except IndexError:
            return
        name = str(uuid4())
        g_tts.save(f"{config['tts_folder']}/{name}.mp3")
        self.voice_client.play(
            discord.FFmpegPCMAudio(f"./{config['tts_folder']}/{name}.mp3")
        )


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
