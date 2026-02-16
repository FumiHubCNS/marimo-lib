# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
#     "marimo-lib",
# ]
#
# [tool.uv.sources]
# marimo-lib = { git = "https://github.com/FumiHubCNS/marimo-lib" }
# ///

import marimo

__generated_with = "0.19.9"
app = marimo.App(
    width="medium",
    layout_file="layouts/fit_samples.slides.json",
    auto_download=["html"],
)

with app.setup:
    # Initialization code that runs before all other cells
    import marimo_lib.util as molib
    import marimo_lib.analysis as moana
    from plotly.subplots import make_subplots
    import random
    import numpy as np
    import pandas as pd


@app.cell
def _():
    import marimo as mo

    GLOBAL_FIG_WIDTH:int = 1000
    return GLOBAL_FIG_WIDTH, mo


@app.cell
def _(mo):
    mo.md(r"""
    # Fit Samples

    描画した相関を任意の関数でフィッティングを行うことができる。

    ここではその方法を示す。

    ## 1次元頻度分布のフィッティング

    一般的にヒストグラムの描画は値のリストを渡して描画される。

    この頻度分布の形を関数でフィッティングするためには、まずデータ点に変換する必要がある。

    このライブラリでは、`marimo_lib.util.plot.get_scatter_from_1d`で取得できる。

    戻り値はBinの中心値とカウント数のリスト。

    引数にはBin数と描画範囲を指定できる。

    図と完全一致させる場合は、上記の引数も指定する必要がある。

    フィッティングには`marimo_lib.analisys.fit.fit_function`でおこなう。

    中身は`scipy`の`curve_fit`である。

    必須の引数はデータのリストとフィットさせる関数

    初期値や境界も指定できる。
    """)
    return


@app.cell
def _(GLOBAL_FIG_WIDTH: int):
    _fig = make_subplots(
        rows=1, cols=1,
        vertical_spacing=0.15,
        horizontal_spacing=0.15,
        subplot_titles=(
            ["Histo1"]
        )
    )

    _h = np.random.normal(loc=0, scale=1, size=100000)

    _x, _y = molib.plot.get_scatter_from_1d(_h, bin=200, range=[-4, 4])
    _v, _e = moana.fit.fit_function([_x, _y], moana.fit.gauss, debug=True)

    _x = np.linspace(-4,4,100)
    _y = moana.fit.gauss(_x, *_v)

    molib.plot.add_sub_plot(
        _fig, 1, 1,
        data=[_h],
        func=molib.plot.go_Histogram,
        xrange=[-4, 4, 0.04],
        dataname="sample"
    )

    molib.plot.add_sub_plot(
        _fig, 1, 1,
        data=[_x, _y],
        func=molib.plot.go_Scatter,
        mode="lines",
        width=2,
        dataname="fit"
    )

    _fig.update_layout(height=400, width=GLOBAL_FIG_WIDTH, showlegend=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 二次元頻度分布のフィッティング

    同様に以下のようにして二次元相関のフィッティングも可能である。
    """)
    return


@app.cell
def _(GLOBAL_FIG_WIDTH: int):
    _x = np.random.uniform(-1, 1, 50000)
    _y = moana.fit.pol1(_x , b=0.0 , a=-1.0)

    _nx = np.random.normal(0, 0.1, size=_x.shape)
    _ny = np.random.normal(0, 0.1, size=_y.shape)

    _x = _x + _nx
    _y = _y + _ny

    _fig = make_subplots(
        rows=1, cols=2,
        vertical_spacing=0.15,
        horizontal_spacing=0.15,
        subplot_titles=(
            ["Histo1", "Histo2"]
        )
    )

    molib.plot.add_sub_plot(
        _fig, 1, 1,
        data=[_x, _y],
        func=molib.plot.go_Heatmap
    )

    molib.plot.add_sub_plot(
        _fig, 1, 2,
        data=[_x+_y],
        func=molib.plot.go_Histogram,
        xrange=[-0.5, 0.5, 0.005]
    )

    _fpv, _fpe = moana.fit.fit_function([_x, _y], moana.fit.pol1, debug=False)
    _fpx = np.linspace(-1.2, 1.2, 2)
    _fpy = moana.fit.pol1(_fpx, *_fpv)

    _x, _y = molib.plot.get_scatter_from_1d(_x+_y, bin=200, range=[-0.5, 0.5])
    _fgv, _fge = moana.fit.fit_function([_x, _y], moana.fit.gauss, debug=False)
    _fgx = np.linspace(-0.5, 0.5, 200)
    _fgy = moana.fit.gauss(_fgx, *_fgv)

    molib.plot.add_sub_plot(
        _fig, 1, 1,
        data=[_fpx, _fpy],
        func=molib.plot.go_Scatter,
        mode="lines",
        width=2,
        color='red'
    )

    molib.plot.add_sub_plot(
        _fig, 1, 2,
        data=[_fgx, _fgy],
        axes_title=['sum', 'counts'],
        func=molib.plot.go_Scatter,
        mode="lines",
        width=2,
        color='blue'
    )

    molib.plot.align_colorbar(_fig, 20)

    _fig.update_layout(height=500, width=GLOBAL_FIG_WIDTH, showlegend=True)
    return


if __name__ == "__main__":
    app.run()
