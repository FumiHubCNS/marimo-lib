# Marimo用ユーティリティー / Plotly ユーティリティー

解析 → 議事録/スライド作成をシームレスに行うためのライブラリ

パッケージ管理としては[uv](https://docs.astral.sh/uv/)、ノートブック環境としては[marimo](https://marimo.io/)を使用しています。

## Quick Start

まずはuvを入れる。
Macなら`curl`で入れることができます。

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

また`brew install uv`でも入れることができます。

後はこのリポジトリをcloneすればセットアップ完了です。

```shell
https://github.com/FumiHubCNS/marimo-lib.git
cd marimo-lib 
uv sync
```

### Sampleを動かしてみる

notebook以下にサンプルコードがあります。

`marimo`で編集および実行するためには`uv run maimo edit [file path]`で起動できます。

例えば、以下のコマンドを叩けばサンプルをみることができます。

```shell
uv run marimo edit notebook/demo.py
```

## ライブラリとして使う時の使い方

uv自身は以下のコマンドGithubから簡単にライブラリを入れることができます。

```shell
uv add "marimo-lib @ git+https://github.com/FumiHubCNS/marimo-lib"
```
