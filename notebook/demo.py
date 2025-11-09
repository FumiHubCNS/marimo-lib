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
def _():
    return


if __name__ == "__main__":
    app.run()
