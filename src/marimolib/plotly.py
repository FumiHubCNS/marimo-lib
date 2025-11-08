import plotly.graph_objs as go
import numpy as np
from typing import Tuple, Dict, Optional

def get_np_histogram2d(
    data: list = None,
    bins: list = None,
    xrange: list = None,
    yrange: list = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    2Dヒストの生カウントとエッジを返す（plotly では z=counts.T を使う想定）
    """
    if data is None:
        return None
    
    if xrange is None:
        xrange = []

    if yrange is None:
        yrange = []
    
    x = data[0]
    y = data[1]

    x = pd.to_numeric(x, errors='coerce')
    y = pd.to_numeric(y, errors='coerce')

    mask = ~np.isnan(x) & ~np.isnan(y)
    x_clean = x[mask]
    y_clean = y[mask]

    if len(xrange) >= 2 and len(yrange) >= 2:
        counts, xedges, yedges = np.histogram2d(x_clean, y_clean, bins=bins,range=[xrange, yrange])
    else:
        counts, xedges, yedges = np.histogram2d(x_clean, y_clean, bins=bins) 

    return counts, xedges, yedges


def slice_y_hist_by_xbin(
    counts: np.ndarray,
    yedges: np.ndarray,
    xbin_index: int,
    *,
    normalize: bool = False,
) -> Dict[str, np.ndarray]:
    """
    2Dヒストの結果から、指定 x ビンに対応する y の一次元ヒストを取り出す。

    Parameters
    ----------
    counts : shape = (nx, ny)  # np.histogram2d の戻り
    yedges : shape = (ny+1,)
    xbin_index : 0..nx-1 のビン番号
    normalize : True のとき面積1に正規化

    Returns
    -------
    dict: {
      "y_counts": (ny,),      # この x ビンの y 分布のカウント
      "y_edges":  (ny+1,),    # y ビン境界
      "y_centers":(ny,),      # y ビン中心
      "xbin_index": int
    }
    """
    nx, ny = counts.shape
    if not (0 <= xbin_index < nx):
        raise IndexError(f"xbin_index out of range: 0..{nx-1}")

    y_counts = counts[xbin_index, :].astype(float)  # 注意：counts は (nx, ny)

    if normalize and y_counts.sum() > 0:
        y_counts = y_counts / y_counts.sum()

    y_centers = 0.5 * (yedges[:-1] + yedges[1:])
    return {
        "counts": y_counts,
        "edges": yedges,
        "centers": y_centers,
        "index": int(xbin_index),
    }

def slice_y_hist_by_xrange(
    x: np.ndarray,
    y: np.ndarray,
    *,
    xedges: np.ndarray,
    ybins: int | np.ndarray,
    x_range: Tuple[float, float],
    normalize: bool = False,
) -> Dict[str, np.ndarray]:
    """
    点群から直接“x の数値範囲”でフィルタし、y の一次元ヒストを作る版。
    （ビン番号ではなく実値レンジで指定したいとき用）

    Parameters
    ----------
    x, y : 元データ
    xedges : x のビン境界（2Dヒストと合わせるなら同じものを渡す）
    ybins : y のビン数 or エッジ配列
    x_range : (xmin, xmax) で半開区間 [xmin, xmax) を想定
    normalize : True のとき面積1に正規化
    """
    xmin, xmax = x_range
    mask = (x >= xmin) & (x < xmax)
    y_sel = y[mask]

    y_counts, yedges = np.histogram(y_sel, bins=ybins)
    if normalize and y_counts.sum() > 0:
        y_counts = y_counts / y_counts.sum()
    y_centers = 0.5 * (yedges[:-1] + yedges[1:])
    return {
        "counts": y_counts,
        "edges": yedges,
        "centers": y_centers,
        "range": np.array([xmin, xmax]),
    }


def add_sub_plot(
        fig,
        irow:int = 1,
        icol:int = 1, 
        plot_type="1d",
        data:list = None,
        labels:list = None,
        bins=[200,200],
        logsf:str = None,
        xrange:list = None,
        yrange:list = None,
        debug:bool = False,
        legends:list = None,
        dataname:str = None,
        color:str = None,
        colormap:str = "Viridis"
):

    if data is None:
        data = []

    if labels is None:
        labels = []

    if bins is None:
        bins = [200, 200]

    if logsf is None:
        logs = [False, False, False]
    else:
        logs = []
        for i in range(3):
            val_bool = True if logsf[i] == "1" else False
            logs.append(val_bool)

    if xrange is None:
        xrange = []

    if yrange is None:
        yrange = []

    xtype = '-' if logs[0] is False else 'log'
    ytype = '-' if logs[1] is False else 'log'
 
    if plot_type == '1d':
        if len(xrange) < 2:
            fig.add_trace(
                go.Histogram(x=data[0],nbinsx=bins[0],name=dataname),
                row=irow, col=icol
            )
        else:
            fig.add_trace(
                go.Histogram(
                    x=data[0],
                    xbins=dict(
                        start=xrange[0],   
                        end=xrange[1], 
                        size=xrange[2] 
                    ),
                    name=dataname
                ),
                row=irow, col=icol
            )

    elif plot_type == '2d': 
        counts, xedges, yedges = get_np_histogram2d(data=data, bins=bins, xrange=xrange, yrange=yrange)

        if logs[2]:
            counts = np.log10(counts + 1)

        bar_title = "ln(+1)" if logs[2] else "Count" 

        xcenters = 0.5 * (xedges[:-1] + xedges[1:])
        ycenters = 0.5 * (yedges[:-1] + yedges[1:])

        heatmap = go.Heatmap(
            x=xcenters,
            y=ycenters,
            z=counts.T,
            colorscale=colormap,
            colorbar=dict(
                title=bar_title
            ),
            name=dataname
        )
        
        fig.add_trace(heatmap, row=irow, col=icol)

        rows_range, cols_range = fig._get_subplot_rows_columns()
        nrows = len(rows_range)
        ncols = len(cols_range)

        index = (irow - 1) * ncols + (icol - 1)
        base_title = fig.layout.annotations[index].text 
        fig.layout.annotations[index].text = f"{base_title}, Entries:{int(counts.sum())}"

        if debug:
            total_count = counts.sum()

            max_val = counts.max()
            max_index = np.unravel_index(np.argmax(counts), counts.shape)
            iy, ix = max_index

            xcenters = 0.5 * (xedges[:-1] + xedges[1:])
            ycenters = 0.5 * (yedges[:-1] + yedges[1:])

            x_at_max = xcenters[ix]
            y_at_max = ycenters[iy]

            min_val = counts.min()
            min_index = np.unravel_index(np.argmin(counts), counts.shape)
            iy, ix = min_index

            x_at_min = xcenters[ix]
            y_at_min = ycenters[iy]

            print(f"[debug] Entries {total_count}, Max value {max_val} at ({x_at_max},{y_at_max}), Min value {min_val} at ({x_at_min},{y_at_min})")
    
    elif plot_type == 'scatter':
        if color is not None:
            fig.add_trace(
                go.Scatter(
                    y = data[0],
                    mode = 'lines+markers',
                    marker = dict(size = 4, color = color),
                    line = dict(width = 1, color = color),
                    name = dataname
                ),
                row=irow, col=icol
            )
        else:
            fig.add_trace(
                go.Scatter(
                    y = data[0],
                    mode = 'lines+markers',
                    marker = dict(size = 4),
                    line = dict(width = 1),
                    name = dataname
                ),
                row = irow,
                col = icol
            )            

    elif plot_type == 'fit':
        if color is not None:
            fig.add_trace(
                go.Scatter(
                    x = data[0],
                    y = data[1],
                    mode = 'lines',
                    marker = dict(
                        size = 4,
                        color = color
                    ),
                    line = dict(
                        width = 2,
                        color = color
                    ),
                    name = dataname
                ),
                row = irow,
                col = icol,
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x = data[0],
                    y = data[1],
                    mode = 'lines',
                    marker = dict(size = 4),
                    line = dict(width = 2),
                    name = dataname
                ),
                row = irow,
                col = icol,
            )

    elif plot_type == 'plot':
        if color is not None:
            fig.add_trace(
                go.Scatter(
                    x = data[0],
                    y = data[1],
                    mode = 'markers',
                    marker = dict(
                        size = 8,
                        color = color
                    ),
                    line = dict(
                        width = 1,
                        color = color
                    ),
                    name = dataname),
                row = irow, 
                col = icol
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x = data[0],
                    y = data[1],
                    mode = 'markers',
                    marker = dict(size = 8),
                    line = dict(width = 1),
                    name = dataname
                ),
                row = irow,
                col = icol
            )

    elif plot_type == 'spark-hist':
        fig.add_trace(
            go.Bar(
                x = data[0],
                y = data[1],
                name = dataname
            ),
            row = irow,
            col = icol
        )
    
    elif plot_type == 'error':
        if color is not None:
            fig.add_trace(
                go.Scatter(
                    x = data[0],
                    y = data[1],
                    mode = "markers",
                    name = dataname,
                    error_y = dict(
                        type = "data",
                        array = data[3],
                        arrayminus = data[2],
                        visible = True
                    )
                ),
                row = irow,
                col = icol
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x = data[0],
                    y = data[1],
                    mode="markers",
                    marker = dict(size = 4),
                    line = dict(width = 1),
                    name = dataname,
                    error_y = dict(
                        type="data",
                        array = data[3],
                        arrayminus = data[2],
                        visible = True
                    )
                ),
                row = irow,
                col = icol
            )      

    if len(labels) >=2:
        fig.update_xaxes(
            type = xtype,
            title_text = labels[0],
            row = irow,
            col = icol
        )

        fig.update_yaxes(
            type = ytype,
            title_text = labels[1],
            row = irow,
            col = icol
        )

    if legends is not None:
        if len(legends) > 5:
            fig.update_layout(
                legend=dict(
                    x = legends[0],
                    y = legends[1],   
                    xanchor = legends[2],
                    yanchor = legends[3],
                    orientation = legends[4]  
                ),
                margin=dict(r = legends[5])               
        )

def align_colorbar(fig, thickness=20, thicknessmode="pixels"):
    for trace in fig.data:
        if isinstance(trace, go.Heatmap):
            xaxis = "xaxis" if trace.xaxis == "x" else "xaxis" + trace.xaxis[1:]
            yaxis = "yaxis" if trace.yaxis == "y" else "yaxis" + trace.yaxis[1:]

            xa = fig.layout[xaxis].domain
            ya = fig.layout[yaxis].domain

            trace.update(colorbar=dict(thickness=thickness, thicknessmode=thicknessmode, x=xa[1] + 0.01, y=(ya[0] + ya[1]) / 2, len=ya[1] - ya[0]))
