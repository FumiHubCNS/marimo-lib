import marimo

__generated_with = "0.17.7"
app = marimo.App(
    width="medium",
    layout_file="layouts/demo.slides.json",
    auto_download=["html"],
)

with app.setup:
    # Initialization code that runs before all other cells
    import marimo_lib as molib
    from plotly.subplots import make_subplots
    import random
    import numpy as np
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
    schedule = molib.schedule.add_periodic_task(
        data=None,
        task="朝会",
        start="2025-10-01 09:00",
        end="2025-10-03 09:00",
        resource="TeamA",
        name="デイリースタンドアップ",
        repeat_until="2025-11-30 23:59",
        every=15,       # 1日ごと
        unit="D",      # 日
        seq_col="StandupNo",
        Owner="TeamA",  # 追加カラムの例
    )

    schedule = molib.schedule.add_periodic_task(
        data=schedule,
        task="進捗会議",
        start="2025-10-03 14:00",      # 1回目（金曜日）
        end="2025-10-03 18:00",
        resource="Meeting",
        name="週次進捗会議",
        repeat_until="2025-11-30 23:59",
        every=7,       # 7日ごと＝週1
        unit="D",
        seq_col="WeeklyNo",
        Room="会議室A",
    )

    schedule = molib.schedule.add_periodic_task(
        data=schedule,
        task="監視チェック",
        start="2025-10-09 12:00",
        end="2025-10-10 12:00",
        resource="Monitoring",
        name="監視チェック",
        repeat_until="2025-11-30 23:59",
        every=14,       # 2時間ごと
        unit="D",      # 時間
        seq_col="MonCheckID",
    )

    schedule = molib.schedule.add_task(
        data=schedule,
        Task="リリース作業",
        Start="2025-10-01 20:00",
        End="2025-10-06 23:00",
        Resource="Release",
        Name="v1.0 リリース",
        Priority=1,
        Owner="ReleaseTeam",
    )

    schedule = molib.schedule.add_task(
        data=schedule,
        Task="リリース作業",
        Start="2025-10-30 20:00",
        End="2025-11-08 23:00",
        Resource="Release",
        Name="v1.1 リリース",
        Priority=1,
        Owner="ReleaseTeam",
    )

    schedule = molib.schedule.add_task(
        data=schedule,
        Task="リリース作業",
        Start="2025-11-15 20:00",
        End="2025-11-30 23:00",
        Resource="Release",
        Name="v1.2 リリース",
        Priority=1,
        Owner="ReleaseTeam",
    )


    mo.vstack([
        mo.md(
            """
            ### `schedule.py`

            スケジュール表示用の関数群。
            `add_task`や`add_periodic_task`などで`pandas.Dataframe`のタスク群を生成

            - `add_periodic_task`は`add_task`を周期的に実行
            - ベースとなる列はあるが、ユーザー独自の列を追加できるようになっている。
            """
        ),
        schedule.head(20)
    ])
    return (schedule,)


@app.cell
def _(GLOBAL_FIG_WIDTH: int, mo, schedule):
    values = schedule["Resource"].unique().tolist()

    timeline_info = dict(
        x_start="Start",
        x_end="End",
        y="Resource",
        color="Resource",
        text="Name",
    )

    fill_palette = molib.schedule.get_color_list('tab10',0.3)
    edge_palette = molib.schedule.get_color_list('tab10',0.9)

    fill_map = dict(zip(values, fill_palette))
    edge_map = dict(zip(values, edge_palette))
    line_map = dict(color=molib.schedule.get_color_list('tokyo',0.8)[0], width=2, dash="dot")
    taskname_map = dict(size=14, color="#b0b0b0")
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
        _fig.update_layout(height=600, width=GLOBAL_FIG_WIDTH, showlegend=False, title_text="Carender")
    ])
    return


@app.cell
def _(mo):
    widget = mo.ui.anywidget(Draw(width=600, height=400))

    mo.vstack([
        mo.md(
            """
            ### Draw.io likeなお絵描きツール

            - スライドや議事録用ノートとしてGUI上で図形を配置したり、文字書いたりするのは重要
            - Draw.ioがあると良いが対応していない。
            - OSSでかつ`marimo`で使えるのは`modarw`のみ
            """
        ),
        widget
    ])
    return (widget,)


@app.cell
def _(mo, widget):
    mo.hstack([
        img(src=widget.value["base64"]),  # Use base64 representation directly with mohtml
        widget.get_pil()                  # Retreive the Python PIL object instead
    ])
    return


@app.cell
def _():
    # widget.value["base64"] = 'data:image/png;base64,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'
    return


@app.cell
def _(widget):
    widget
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
