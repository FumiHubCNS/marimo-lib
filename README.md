# Marimo用ユーティリティー / Plotly ユーティリティー

解析 → 議事録/スライド作成をシームレスに行うためのライブラリ

パッケージ管理としてはuv、ノートブック環境としてはmarimoを使用しています。

## Quick Start

uvを入れる。Macなら`brew`でOK

```shell
brew install uv
```

後はこのリポジトリをcloneすればOK

```shell
https://github.com/FumiHubCNS/marimo-lib.git
cd marimo-lib 
uv sync
```

### Sampleを動かしてみる

以下のコマンドを叩けばOK

```shell
uv run marimo edit notebook/demo.py
```

## ライブラリとして使う時の使い方

uv自身は以下のコマンドGithubから簡単にライブラリを入れることができる。

```shell
uv add "marimo-lib @ git+https://github.com/FumiHubCNS/marimo-lib"
```
