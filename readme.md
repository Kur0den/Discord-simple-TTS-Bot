# 簡易 TTSBot

## 動作環境

Python3.11.4 で動作確認済み

3.12.x では多分動きません

## 使い方

1. Discord の Bot のトークンを発行して使用するサーバーに招待します
2. `git clone https://github.com/Kur0den/Discord-simple-TTS-Bot`でこのリポジトリを clone します
3. `config.json.example`を`config.json`に変更して中の値（トークン・サーバー ID・必要であれば読み上げ文字上限）を編集します
4. venv なりなんなりで`Python3.11.xx`の環境を用意します
5. 用意した環境で`((py/pyhthon) -m )pip install -r requirements.txt`を実行して依存関係をインストールします
6. あと ffmpeg をインストールして Path を通しておきます
7. `main.py`を実行します
8. Discord 上で`(config.jsonで指定したprefix) jsk sync (サーバーID)`を実行してコマンドを同期します
9. 多分これで使えます

## コマンド

-   `[設定したPrefix] ping`
    Ping です
    生存確認ができます
-   `[設定したPrefix] jishaku`
    Jishaku が使えます
    くわしくは[ここ](https://jishaku.readthedocs.io/en/latest/)をみてね
-   `/connect`
    実行した VC のチャンネルに接続してそのチャンネルに投稿されたメッセージを読み上げます
-   `/stop`
    読み上げを全部止めます
-   `/disconnect`
    VC から切断します

質問とか？あれば[@Kur0den0010@koliosky.com](https://koliosky.com/`kur0den0010)まで DM でもリプライでもいいのでください

できる限り答えます
