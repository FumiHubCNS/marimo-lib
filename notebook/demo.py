import marimo

__generated_with = "0.17.7"
app = marimo.App(width="medium", layout_file="layouts/demo.slides.json")


@app.cell
def _():
    import marimo as mo
    import marimo_lib as molib
    from plotly.subplots import make_subplots

    import random
    import numpy as np

    GLOBAL_FIG_WIDTH:int = 1250
    return GLOBAL_FIG_WIDTH, make_subplots, mo, molib, np, random


@app.cell
def _(mo, molib):
    html_test = molib.image.get_image_html("notebook/figs/logotype-wide.png")

    mo.vstack([
        mo.md(
            """
            ## 自作関数の使い方

            ### `image.py`

            図の描画に関する関数群。
            最終的にはHTMLで保存を行いたいので図を挿入する際はマークダウン記法で書かず`base64`にてHTMLテキストにして変数に格納する。

            `mo.Html(html_test)`にて描画

            """
        ),
        mo.Html(html_test)
    ])
    return


@app.cell
def _(GLOBAL_FIG_WIDTH: int, make_subplots, mo, molib, np, random):
    def gauss(
        x,
        a:float = 1.,
        mu:float = 0.,
        sigma:float = 1.
    ):
        return a*np.exp(-(x-mu)**2 / (2.*sigma**2))


    _x  = np.linspace(-5,5,100)
    _y  = gauss(_x, a=10)
    _el = _y/_y
    _eu = _y/_y

    for _i in range(len(_el)):
        _el[_i] = random.random()
        _eu[_i] = random.random()

    x_2d = np.random.normal(loc=0, scale=3, size=1000000)
    y_2d = np.random.rayleigh(scale=1, size=1000000)

    fig = make_subplots(rows=1, cols=2, vertical_spacing=0.15, horizontal_spacing=0.15, subplot_titles=(["1D Gaussian","2D Gaussian"]))
    molib.plot.add_sub_plot(fig, 1, 1, 'error', [_x, _y, _el, _eu], [f'Variable', f'Value'], dataname='Data')
    molib.plot.add_sub_plot(fig, 1, 2, '2d', [x_2d, y_2d], ['X', 'Y'], [200, 200], None, colormap='Turbo')

    mo.vstack([
        mo.md(
            """
            ### `plot.py`

            plotlyの描画に関する関数群。
            `plotly.graph_objects.Figure`のインスタンスを生成する部分は`plotly`の関数を使って宣言する。

            各々のsub plotに描画する際は`plot.add_sub_plot`を用いてスタックしていくことで描画できる。
            """
        ),
        fig.update_layout(height=500, width=GLOBAL_FIG_WIDTH, showlegend=False, title_text="")
    ])
    return fig, x_2d, y_2d


@app.cell
def _(GLOBAL_FIG_WIDTH: int, make_subplots, mo, molib, x_2d, y_2d):
    _data_x = molib.plot.get_slice_array([x_2d, y_2d], [200, 200], slice_axis='x', bin_span=50)
    _data_y = molib.plot.get_slice_array([x_2d, y_2d], [200, 200], slice_axis='y', bin_span=50)

    _fig = make_subplots(
        rows=1, cols=2, vertical_spacing=0.15, horizontal_spacing=0.15,
        subplot_titles=(
            [
                "1D Rayleigh distribution",
                "1D Gaussian distribution"
            ]
        )
    )

    _data = _data_x

    for _i in range(len(_data)):
        molib.plot.add_sub_plot(
            _fig, 1, 1, 'plot', [_data[_i]['centers'], _data[_i]['counts']], [f'Variable', f'Value'], logsf='000',
            dataname=f'{_data[_i]["axis"]}-slice({_data[_i]["bin_index"]}:{_data[_i]["bin_index"]+_data[_i]["bin_span"]})'
        )

    _data = _data_y

    for _i in range(len(_data)):
        molib.plot.add_sub_plot(
            _fig, 1, 2, 'plot', [_data[_i]['centers'], _data[_i]['counts']], [f'Variable', f'Value'], logsf='000',
            dataname=f'{_data[_i]["axis"]}-slice({_data[_i]["bin_index"]}:{_data[_i]["bin_index"]+_data[_i]["bin_span"]})'
        )

    mo.vstack([
        mo.md(
            """
            #### 二次元ヒストグラムをスライス

            `plot.get_slice_array`にて実行可能。
            - `slice_axis`, `bin_span`でスライス方向とRebinの数を調整できる。
            - `histo_skip`で`numpy.histogram2d(...)`をスキップするかを選択可能。
            """
        ),
        _fig.update_layout(height=500, width=GLOBAL_FIG_WIDTH, showlegend=True, title_text="Slice data")
    ])
    return


@app.cell
def _(GLOBAL_FIG_WIDTH: int, fig, make_subplots, mo, molib):
    _output_path = molib.plot.save_fig_as_html(fig, 'notebook/figs/plot.html')
    _output_html = molib.plot.load_html_as_str(_output_path)
    _output_data = molib.plot.get_plotly_values_json(_output_html)
    _output_valu = molib.plot.decode_typed_arrays(_output_data[0][0])

    _fig = make_subplots(rows=1, cols=1, vertical_spacing=0.15, horizontal_spacing=0.15, subplot_titles=(["Data extracted from HTML"]))
    molib.plot.add_sub_plot(
        _fig, 1, 1, 'error', 
        [
            _output_valu['x'],
            _output_valu['y'],
            _output_valu['error_y']['array'],
            _output_valu['error_y']['arrayminus']  
        ], 
        [f'Variable', f'Value'], dataname='Data'
    )

    mo.vstack([
        mo.md(
            """
            #### HTMLからデータを保存・抽出

            - `plot.save_fig_as_html`にて保存可能
              - 第一引数に`plotly.graph_objects.Figure`のインスタンス、第二引数にパスを指定することで保存
              - 戻り値としてファイルのパスが返ってくる。
            - `plot.load_html_as_str`で保存したHTMLをString型として取得
            - `plot.get_plotly_values_json`および`plot.decode_typed_arrays`にてデータを値を取得
              - HTML保存時の保存形式が選択不可: 数値が格納されている場合は`plot.get_plotly_values_json`のみでよい
              - そうでない場合は`plot.get_plotly_values_json`で取得した辞書またはタプルを引数に`plot.decode_typed_arrays`に渡す。 
            """
        ),
        mo.md("→" + " " + "x[0:5]:" + " " + str(molib.plot.decode_typed_arrays(_output_valu['x'])[0:5])),
        mo.md("→" + " " + "y[0:5]:" + " " + str(molib.plot.decode_typed_arrays(_output_valu['y'])[0:5])),
        _fig.update_layout(height=300, width=GLOBAL_FIG_WIDTH, showlegend=False, title_text="")
    ])
    return


@app.cell
def _(make_subplots):
    import plotly.graph_objects as go
    import pandas as pd
    import datetime as dt
    # from plotly.subplots import make_subplots
    # import numpy as np


    # df = pd.DataFrame([
    #     {"task": "Task D", "start": "2025-01-01", "finish": "2025-01-05", "group": "Line 2"},
    #     {"task": "Task A", "start": "2025-01-07", "finish": "2025-01-10", "group": "Line 1"},
    #     {"task": "Task B", "start": "2025-01-03", "finish": "2025-01-08", "group": "Line 1"},
    #     {"task": "Task C", "start": "2025-01-02", "finish": "2025-01-06", "group": "Line 2"},
    #     {"task": "Task D", "start": "2025-01-09", "finish": "2025-01-10", "group": "Line 2"},
    # ])

    # df["start"]  = pd.to_datetime(df["start"])
    # df["finish"] = pd.to_datetime(df["finish"])

    # df["duration_days"] = (df["finish"] - df["start"]).dt.total_seconds() / 86400.0

    df = pd.DataFrame([
        {"task": "Task D", "start": "2025-01-01", "finish": "2025-01-05", "group": "Line 2"},
        {"task": "Task A", "start": "2025-01-07", "finish": "2025-01-10", "group": "Line 1"},
        {"task": "Task B", "start": "2025-01-03", "finish": "2025-01-08", "group": "Line 1"},
        {"task": "Task C", "start": "2025-01-02", "finish": "2025-01-06", "group": "Line 2"},
        {"task": "Task E", "start": "2025-01-09", "finish": "2025-01-10", "group": "Line 2"},
    ])

    df["start"]  = pd.to_datetime(df["start"])
    df["finish"] = pd.to_datetime(df["finish"])
    df["duration_days"] = (df["finish"] - df["start"]).dt.total_seconds() / 86400.0


    _fig = make_subplots(
        rows=1, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=("Line 1", "Line 2"),
    )

    _i = 0

    _fig.add_trace(
        go.Bar(
            # ★ x は「終了日時」
            x=[df["finish"][_i]],
            base=[df["start"][_i]],
            y=[df["task"][_i]],
            orientation="h"
        ),
        row=1, col=1,
    )

    _i = 4

    _fig.add_trace(
        go.Bar(
            # ★ x は「終了日時」
            x=[df["finish"][_i]],
            base=[df["start"][_i]],
            y=[df["task"][_i]],
            orientation="h"
        ),
        row=1, col=1,
    )

    # for row, grp in enumerate(["Line 1", "Line 2"], start=1):
    #     sub = df[df["group"] == grp]

    #     _fig.add_trace(
    #         go.Bar(
    #             # ★ x は「終了日時」
    #             x=sub["finish"],
    #             # ★ base は「開始日時」
    #             base=sub["start"],
    #             y=sub["task"],
    #             orientation="h",
    #             text=[f"{s.date()} → {f.date()} ({d:.1f} d)"
    #                   for s, f, d in zip(sub["start"], sub["finish"], sub["duration_days"])],
    #             hovertemplate=(
    #                 "Task: %{y}<br>"
    #                 "Start: %{base}<br>"
    #                 "Finish: %{x}<br>"
    #                 "Duration: %{text}<extra></extra>"
    #             ),
    #         ),
    #         row=1, col=1,
    #     )

    # for task, sub in df.groupby("task"):
    #     _fig.add_trace(
    #         go.Bar(
    #             x=sub["finish"],
    #             base=sub["start"],
    #             y=[task] * len(sub),  # 同じ task 名を繰り返す
    #             orientation="h",
    #             name=task,
    #         )
    #     )

    _fig.update_xaxes(type="date", row=1, col=1)
    _fig.update_xaxes(type="date", row=2, col=1)


    xmin = df["start"].min() - pd.Timedelta(days=1)
    xmax = df["finish"].max() + pd.Timedelta(days=1)

    _fig.update_xaxes(range=[xmin, xmax], row=1, col=1)
    _fig.update_xaxes(range=[xmin, xmax], row=2, col=1)

    _fig.update_layout(
        barmode="overlay",
        showlegend=False,
    )

    _fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        griddash="dot",  # 破線にしたいとき（plotly>=5系なら使える）
        row=1, col=1
    )




    deadline = dt.datetime(2025, 1, 6)

    _fig.add_vline(
        x=deadline,
        line=dict(color="red", width=2, dash="dot"),
        row=1, col=1
    )



    # _fig.add_annotation(
    #     x=deadline,
    #     y=1.05,  # 軸外（1よりちょい上）に出したい場合 → yref="paper" と併用
    #     xref="x",       # x は第1サブプロットの x軸、という意味
    #     yref="paper",   # 図全体の縦方向 0〜1
    #     text="Deadline",
    #     showarrow=True,
    #     arrowhead=2,
    #     ax=0,
    #     ay=-30,         # 矢印の向き
    #     font=dict(color="red"),
    #     row=1, col=1,
    # )

    _fig.show()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
