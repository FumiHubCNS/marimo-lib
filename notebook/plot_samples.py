import marimo

__generated_with = "0.17.7"
app = marimo.App(width="full", auto_download=["html"])

with app.setup:
    # Initialization code that runs before all other cells
    import marimo as mo
    import marimo_lib.util as molib
    from plotly.subplots import make_subplots
    import numpy as np


@app.cell
def _():
    mo.md(r"""
    # Plotlyベースで図を描画する例

    基本的にはコード内でplotlyの`plotly.graph_objects.Figure`を生成し、そのインスタンスを`marimo_lib.util.plot.add_sub_plot`に渡しながら図を加えていきます。

    この関数の引数は以下のようになっています。

    ```python
    fig: go.Figure,
    irow: int=1,
    icol: int=1,
    data: list | None=None,
    axes_title: list | None=None,
    log_option: str | list | None=None,
    legend_option: list | None=None,
    func: Callable[..., Any] | None=None,
    **kwargs
    ```

    `func`関数以前の引数は`fig`のレイアウトに関するもので、これらの引数でレイアウトを指定し、`func`および、その後に`func`の引数を入れてあげることで描画かできます。

    このライブラリには`func`として

    - `go_Histogram`
    - `go_Heatmap`
    - `go_Scatter`
    - `go_Bar`

    が実装されており、どれも基本的にはgo.[Method]を実行しています。

    またこの`func`には自分でも定義可能です。
    """)
    return


@app.cell
def _():
    mo.md(r"""
    ## 以下サンプル

    ### 一次元ヒストグラム

    一次元ヒストグラムは`go_Histogram`か`go_Bar`を使用します。

    リストの値を集計してヒストグラムを作りたい場合は前者、座標データをヒストグラムにしたい場合は後者を利用すればOKです。
    """)
    return


@app.cell
def _():
    _fig = make_subplots(rows=1, cols=2, vertical_spacing=0.15, horizontal_spacing=0.15, subplot_titles=(["Histo1","Histo2"]))

    _x = np.linspace(-15,15,100)
    _y = np.linspace(-15,15,100)

    _h = np.random.normal(loc=0, scale=3, size=1000000)

    molib.plot.add_sub_plot(_fig, 1, 1, data=[_h], func=molib.plot.go_Histogram, dataname="sample1")
    molib.plot.add_sub_plot(_fig, 1, 2, data=[_x,_y], func=molib.plot.go_Bar)

    _fig.update_layout(height=500, width=1000, showlegend=True)
    return


@app.cell
def _():
    mo.md(r"""
    ### 二次元ヒストグラム

    こちらの場合は、`go_Heatmap`を使います。

    この関数の中では`no.histogram2d`が実行されており、渡すデータ列の数によって挙動が異なります。

    2列渡した場合は、行ごとの座標を集計します。
    一方で3列渡した場合は、3列目を重みとしてマップが作成されます。
    すなわち、x,y,zの値を渡すとx,y平面上にzの値を色として表示するような感じになります。
    """)
    return


@app.cell
def _():
    _fig = make_subplots(rows=1, cols=2, vertical_spacing=0.15, horizontal_spacing=0.15, subplot_titles=(["Histo1","Histo2"]))


    _x = np.random.normal(loc=0, scale=3, size=1000000)
    _y = np.random.normal(loc=0, scale=3, size=1000000)

    molib.plot.add_sub_plot(_fig, 1, 1, data=[_x,_y],func=molib.plot.go_Heatmap, logz_option=True)

    _x = [0,0,0,1,1,1,2,2,2]
    _y = [0,0,0,1,1,1,2,2,2]
    _z = [0,1,0,1,2,1,0,1,0]

    molib.plot.add_sub_plot(_fig, 1, 2, data=[_x,_y,_z], func=molib.plot.go_Heatmap, colormap='mint')
    molib.plot.align_colorbar(_fig, thickness=20)

    _fig.update_layout(height=500, width=1000, showlegend=True)
    return


@app.cell
def _():
    mo.md(r"""
    ### 散布図や線、エラーバー付きグラフ

    `go_Scatter`を使います。
    こちらはオプション次第で、線にしたり、対称(非対称)エラーバーにしたりできます。
    また`x_error`という引数もあり、x軸のエラーもつけられます。
    """)
    return


@app.cell
def _():
    _fig = make_subplots(
        rows=2, cols=2, vertical_spacing=0.2, horizontal_spacing=0.15, 
        subplot_titles=(
            [
                "Scatter plot with 1d data",
                "Scatter plot with 2d data",
                "Scatter plot with symetric error",
                "Scatter plot with asymetric error",
            ]
        )
    )

    _x = np.linspace(0,30,30)
    _y = np.random.normal(loc=0, scale=3, size=30)

    _eu = np.random.uniform(low=0, high=1, size=30)
    _ed = np.random.uniform(low=0, high=1, size=30)

    molib.plot.add_sub_plot(_fig, 1, 1, data=[_x,_y],func=molib.plot.go_Scatter, mode='lines')
    molib.plot.add_sub_plot(_fig, 1, 2, log_option='11',data=[_x],func=molib.plot.go_Scatter)

    molib.plot.add_sub_plot(_fig, 2, 1, data=[_x,_y],func=molib.plot.go_Scatter, y_error=[_eu], mode='lines+markers', width =2 )
    molib.plot.add_sub_plot(_fig, 2, 2, data=[_x,_y],func=molib.plot.go_Scatter, y_error=[_eu, _ed], color='black')

    _fig.update_layout(height=600, width=1000, showlegend=False, title_text="scatter plots")
    return


if __name__ == "__main__":
    app.run()
