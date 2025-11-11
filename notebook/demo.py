import marimo

__generated_with = "0.17.7"
app = marimo.App(
    width="full",
    layout_file="layouts/demo.slides.json",
    auto_download=["html"],
)

with app.setup:
    # Initialization code that runs before all other cells
    import marimo_lib.util as molib
    from plotly.subplots import make_subplots
    import random
    import numpy as np
    import pandas as pd
    from modraw import Draw
    from mohtml import img
    from pathlib import Path
    import base64


@app.cell
def _(mo):
    mo.md(r"""
    # Demo

    このライブラリのサンプルをここに示す。
    """)
    return


@app.cell
def _():
    import marimo as mo

    GLOBAL_FIG_WIDTH:int = 1250
    return GLOBAL_FIG_WIDTH, mo


@app.cell
def _(mo):
    html_test = molib.image.get_image_html("notebook/figs/logotype-wide.png")

    mo.vstack([
        mo.md(
            """
            ## 自作関数の使い方

            ### `image.py`

            図の描画に関する関数群。
            最終的にはHTMLで保存を行いたいので図を挿入する際はマークダウン記法で書かず`base64`にてHTMLテキストにして変数に格納する。

            `mo.Html(html_test)`にて描画

            <br>

            """
        ),
        mo.Html(html_test)
    ])
    return


@app.function
def gauss(
    x,
    a:float = 1.,
    mu:float = 0.,
    sigma:float = 1.
):
    return a*np.exp(-(x-mu)**2 / (2.*sigma**2))


@app.cell
def _(GLOBAL_FIG_WIDTH: int, mo):
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
def _(GLOBAL_FIG_WIDTH: int, mo, x_2d, y_2d):
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
def _(GLOBAL_FIG_WIDTH: int, fig, mo):
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
def _(mo):
    schedule = molib.schedule.init_schedule()

    molib.schedule.add_periodic_task(
        data=schedule,
        task="朝会",
        start="2025-10-01 09:00",
        end="2025-10-03 09:00",
        resource="TeamA",
        name="デイリースタンドアップ",
        repeat_until="2025-11-30 23:59",
        every=15,
        unit="D",
        seq_col="StandupNo",
        owner="TeamA",
    )

    molib.schedule.add_periodic_task(
        data=schedule,
        task="進捗会議",
        start="2025-10-03 14:00",
        end="2025-10-03 18:00",
        resource="Meeting",
        name="週次進捗会議",
        repeat_until="2025-11-30 23:59",
        every=7, 
        unit="D",
        seq_col="WeeklyNo",
        room="会議室A",
    )

    molib.schedule.add_periodic_task(
        data=schedule,
        task="監視チェック",
        start="2025-10-09 12:00",
        end="2025-10-10 12:00",
        resource="Monitoring",
        name="監視チェック",
        repeat_until="2025-11-30 23:59",
        every=14,
        unit="D",
        seq_col="MonCheckID",
    )

    molib.schedule.add_task(
        data=schedule,
        task="リリース作業",
        start="2025-10-01 20:00",
        end="2025-10-06 23:00",
        resource="Release",
        name="v1.0 リリース",
        priority=1,
        owner="ReleaseTeam",
    )

    molib.schedule.add_task(
        data=schedule,
        task="リリース作業",
        start="2025-10-30 20:00",
        end="2025-11-08 23:00",
        resource="Release",
        name="v1.1 リリース",
        priority=1,
        owner="ReleaseTeam",
    )

    molib.schedule.add_task(
        data=schedule,
        task="リリース作業",
        start="2025-11-15 20:00",
        end="2025-11-30 23:00",
        resource="Release",
        name="v1.2 リリース",
        priority=1,
        owner="ReleaseTeam",
    )

    molib.schedule.add_task_csv(
        data=schedule,
        input_path="notebook/data/schedule.csv",
        func_label="func",
    )


    values = schedule["resource"].unique().tolist()

    mo.vstack([
        mo.md(
            """
            ### `schedule.py`

            スケジュール表示用の関数群。
            `molib.schedule.init_schedule`で初期化（※単純に列のみのからDataframeを返す）。
            `add_task`や`add_periodic_task`などで`pandas.Dataframe`のタスク群を生成。
            csvにスケジュールを書いてそれを読み込むことも可能。`schedule.add_task_csv`を使う。

            - `add_periodic_task`は`add_task`を周期的に実行
            - `schedule.add_task_csv`ではtaskの追加のために使用する関数を書く列が必要。
            - ベースとなる列はあるが、ユーザー独自の列を追加できるようになっている。
            """
        ),
        schedule.head(20)
    ])
    return schedule, values


@app.cell
def _(GLOBAL_FIG_WIDTH: int, mo, schedule, values):
    timeline_info = dict(
        x_start="start",
        x_end="end",
        y="resource",
        color="resource",
        text="name",
    )

    fill_palette = molib.schedule.get_color_list('tab10',0.3)
    edge_palette = molib.schedule.get_color_list('tab10',0.9)

    fill_map = dict(zip(values, fill_palette))
    edge_map = dict(zip(values, edge_palette))
    line_map = dict(color=molib.schedule.get_color_list('tokyo',0.8)[0], width=2, dash="dot")
    taskname_map = dict(size=14, color="#000000")
    _fig = make_subplots(rows=1, cols=1, vertical_spacing=0.15, horizontal_spacing=0.15, subplot_titles=([""]))

    molib.schedule.add_schedule(
        fig = _fig,
        data = schedule,
        timeline_info = timeline_info,
        taskname_info = taskname_map,
        color_discrete_map = fill_map,
        edge_color_map = edge_map,
        line_info =line_map,
        irow = 1,
        icol = 1
    )

    mo.vstack([
        mo.md(
            """
            #### カレンダーの一例

            - `plotly`にはガントチャート用関数は使いにくい。
              - `plotly.express.timeline()`で`Figure`のインスタンス生成
              - `add_trace()`で追加
              -　`marimo_lib.plot`の関数でよく使われる`plotly.graph_objects.Figure`に対応
            - `timeline_info`で表示するタスクのグループやガントチャートのテキストなどを変更できる。
            - `fill_map`, `edge_map`, `line_map`, `taskname_map`などで負荷情報を付与
            """
        ),
        _fig.update_layout(height=500, width=GLOBAL_FIG_WIDTH, showlegend=False, title_text='')
    ])
    return


@app.cell
def _(GLOBAL_FIG_WIDTH: int, mo):
    widget_tl = mo.ui.anywidget(Draw(width=int(GLOBAL_FIG_WIDTH/2), height=600))
    widget_ex = molib.excalidraw.ExcalidrawWidget(width=int(GLOBAL_FIG_WIDTH/2), height=600)

    mo.vstack([
        mo.md(
            """
            ### Draw.io likeなお絵描きツール

            - スライドや議事録用ノートとしてGUI上で図形を配置したり、文字書いたりするのは重要
            - Draw.ioがあると良いが対応していない。
            - `modarw`や`excalidraw`などがある
            """
        ),
        mo.hstack([
            widget_tl,
            widget_ex
        ]),
    ])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
