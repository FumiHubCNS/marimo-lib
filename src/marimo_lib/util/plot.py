try:
    import json5 as _json
except Exception:
    import json as _json

import re
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from typing import Tuple, Dict
from typing import List, Any, Optional
import plotly.io as pio
import base64
import os
import time
from typing import Callable
import inspect

pio.renderers.default = "browser"

def save_fig_as_html(
    fig: go.Figure, 
    savepath: str = "notebook/figs/figure.html"
) -> str:
    """
    Plotlyで作成した図をHTML形式で保存する関数。
    ディレクトリが存在しない場合は自動的に作成し、
    figのタイトルには保存時刻（UNIX秒）を追記する。

    Function to save a Plotly-generated figure as HTML.
    If the directory does not exist, it is automatically created.
    The figure title appends the save time (UNIX timestamp).
    
    Parameters
    ----------
    fig : 
        instance of plotly.graph_objects.Figure
    savepath : 
        Name of output file path

    Returns
    -------
    str : 
        Output file path to the saved HTML file.
    """

    dirpath = os.path.dirname(savepath)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)

    timestamp = int(time.time())

    if hasattr(fig.layout, "title") and fig.layout.title.text:
        fig.update_layout(title=f"{fig.layout.title.text} ({timestamp})")
    else:
        fig.update_layout(title=f"({timestamp})")

    pio.write_html(
        fig,
        file=savepath,
        include_plotlyjs="inline",
        full_html=True,
        auto_open=False,
    )

    return savepath


def load_html_as_str(input_path:str =  "notebook/figs/figure.html") -> str:
    """
    HTMLを読み込む関数

    Load HTML file.

    Parameters
    ----------
    input_path : 
        Input file path 

    Returns
    -------
    str: 
        String型に格納されたHTMLテキスト
    """
    with open(input_path, "r", encoding="utf-8") as f:
        html = f.read()

    return html


def get_plotly_values_json(text):
    """
    String型で格納されているHTMLテキストからデータの値をjson形式でパースする関数
    
    Parse data values from HTML text stored as a String into JSON format.

    Parameters
    ----------
    text : 
        Original HTML text

    Returns
    -------
    parse_plotly_script(script_js): 
       Tupleに格納された、パース済みHTMLテキストのデータとレイアウトの情報
    """
    keyword = "plotly-graph-div"
    pos = text.find(keyword)
    front = find_right_all(text, "<script", pos)[0] 
    back = find_right_all(text, "</script>", pos)[0] 
    script_js = text[front:back+9]

    return parse_plotly_script(script_js)


def parse_plotly_script(script_js: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    <script> 内のテキスト（Plotly.newPlot(...) を含む）から data(list), layout(dict) を返す。
    
    Returns data(list) and layout(dict) from the text within <script> (including Plotly.newPlot(...)).

    Parameters
    ----------
    script_js : 
        Javescript text in string format

    Returns
    -------
    data, layout: 
       Tupleに格納された、パース済みHTMLテキストのデータとレイアウトの情報
    """
    m = re.search(r'Plotly\.newPlot\s*\(', script_js)
    if not m:
        raise ValueError("Plotly.newPlot(...) not found")
    pos = m.end()

    data_json, pos_after_data = extract_bracketed(script_js, pos, '[', ']')
    layout_json, _ = extract_bracketed(script_js, pos_after_data, '{', '}')

    data = _json.loads(data_json)
    layout = _json.loads(layout_json)
    return data, layout


def extract_bracketed(s: str, start_pos: int, open_ch: str, close_ch: str) -> Tuple[str, int]:
    """
    s[start_pos:] で最初の open_ch から対応する close_ch までを括弧対応で抜き出す
    
    Extract the data between close_ch and open_ch using bracket matching with s[start_pos:]

    Parameters
    ----------
    s : 
        Original javascript text extracted by self.get_plotly_values_json
    start_pos : 
        Start position
    open_ch : 
        Start channel 
    close_ch :  
        Close channel 

    Returns
    -------
    s[i:j+1], j+1: 
       Tupleに格納された、パース済みHTMLテキストのデータとレイアウトの情報
    """
    i = s.find(open_ch, start_pos)
    if i < 0:
        raise ValueError(f"opening '{open_ch}' not found after {start_pos}")
    depth = 0
    j = i
    in_str = False
    quote: Optional[str] = None
    esc = False
    while j < len(s):
        ch = s[j]
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                in_str = False
                quote = None
        else:
            if ch in ("'", '"', '`'):
                in_str = True
                quote = ch
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return s[i:j+1], j+1
        j += 1
    raise ValueError(f"no matching '{close_ch}' for '{open_ch}'")


def decode_typed_arrays(obj:Tuple[List[Dict[str, Any]], Dict[str, Any]]):
    """
    Plotlyで保存したHTMLから数値データを取得する関数。
    再帰的に探索し、numpy.ndarrayにデコード
    
    Get numerical data from HTML saved with Plotly.
    Recursively traverse and decode into a numpy.ndarray    

    Parameters
    ----------
    obj : 
        Instance of self.parse_plotly_script()

    Returns
    -------
    output: 
        numpy.ndarray or Tuple[List[Dict[str, Any]], Dict[str, Any]]
    """
    if isinstance(obj, dict) and "dtype" in obj and "bdata" in obj:
        dtype = np.dtype(obj["dtype"])
        raw = base64.b64decode(obj["bdata"])
        arr = np.frombuffer(raw, dtype=dtype)
        # 2次元以上
        shape = obj.get("shape")
        if shape:
            if isinstance(shape, str):
                shape = tuple(int(s) for s in shape.split(","))
            arr = arr.reshape(shape)
        return arr

    if isinstance(obj, list):
        return [decode_typed_arrays(x) for x in obj]

    if isinstance(obj, dict):
        return {k: decode_typed_arrays(v) for k, v in obj.items()}

    return obj


def find_left(text: str, needle: str, from_pos: int, *, include_current: bool=False) -> int:
    """
    text の from_pos 位置から左方向に needle（文字列）を探し、直近の一致の開始位置を返す。
    見つからなければ -1。
    include_current=True にすると、from_pos を含む（=右端が from_pos を超えない）範囲も対象。
    
    Searches for the string needle starting from the position from_pos in text, returning the start position of the closest match.
    Returns -1 if no match is found.
    Setting include_current=True includes the range containing from_pos (i.e., the right edge does not exceed from_pos).

    Parameters
    ----------
    text : 
        Original text
    needle : 
        Target text
    from_pos : 
        Starting position
    include_current :
        Flag for including the outside of search range
        
    Returns
    -------
    int: 
        Start position searched to left direction from from_pos 
    """
    end = from_pos + 1 if include_current else from_pos

    return text.rfind(needle, 0, max(0, end))


def find_left_all(text: str, needle: str, from_pos: int, *, include_current: bool=False) -> List[int]:
    """
    左側（from_pos より左、必要なら含む）にある全一致の開始位置をリストで返す（昇順）。
    
    Return a list of all exact match start positions on the left side (to the left of from_pos, including it if necessary) in ascending order.

    ----------
    text : 
        Original text
    needle : 
        Target text
    from_pos : 
        Starting position
    include_current :
        Flag for including the outside of search range

        
    Returns
    -------
    out: 
        Start position searched to left direction from from_pos 
    """
    end = from_pos + 1 if include_current else from_pos
    out = []
    start = 0

    while True:
        i = text.find(needle, start, end)
        if i == -1:
            break
        out.append(i)
        start = i + 1

    return out


def find_left_regex(text: str, pattern: str, from_pos: int, *, flags: int=0, include_current: bool=False) -> int:
    """
    正規表現で左側の最後の一致開始位置を返す。見つからねば -1。

    Returns the starting position of the last match on the left side using regular expressions. Returns -1 if no match is found.
    
    ----------
    text : 
        Original text
    needle : 
        Target text
    from_pos : 
        Starting position
    include_current :
        Flag for including the outside of search range

    Returns
    -------
    out: 
        Start position searched using regular expressions to left direction from from_pos 
    """
    end = from_pos + 1 if include_current else from_pos
    last_start = -1

    for m in re.finditer(pattern, text[:max(0, end)], flags):
        last_start = m.start()

    return last_start


def find_right(text: str, needle: str, from_pos: int, *, include_current: bool=False) -> int:
    """
    text の from_pos 位置から右方向に needle（文字列）を探し、直近の一致の開始位置を返す。
    見つからなければ -1。
    include_current=True にすると、from_pos を含む（=左端が from_pos を超えない）範囲も対象。
    
    Searches for the string needle starting from the position from_pos in text, returning the start position of the closest match.
    Returns -1 if no match is found.
    Setting include_current=True includes the range containing from_pos (i.e., the left edge does not exceed from_pos).

    Parameters
    ----------
    text : 
        Original text
    needle : 
        Target text
    from_pos : 
        Starting position
    include_current :
        Flag for including the outside of search range

    Returns
    -------
    int: 
        Start position searched to right direction from from_pos 
    """
    start = from_pos if include_current else from_pos + 1

    return text.find(needle, max(0, start))


def find_right_all(text: str, needle: str, from_pos: int, *, include_current: bool=False) -> List[int]:
    """
    右側（from_pos より右、必要なら含む）にある全一致の開始位置をリストで返す（昇順）。
    
    Return a list of all exact match start positions on the right side (to the right of from_pos, including it if necessary) in ascending order.

    ----------
    text : 
        Original text
    needle : 
        Target text
    from_pos : 
        Starting position
    include_current :
        Flag for including the outside of search range

    Returns
    -------
    out: 
        Start position searched to right direction from from_pos 
    """
    start = from_pos if include_current else from_pos + 1
    out = []
    n = len(needle)
    i = text.find(needle, max(0, start))

    while i != -1:
        out.append(i)
        i = text.find(needle, i + max(1, n))  # 重なりを拾わない。重なりも拾うなら +1 にする

    return out


def find_right_regex(text: str, pattern: str, from_pos: int, *, flags: int=0, include_current: bool=False) -> int:
    """
    正規表現で右側の最後の一致開始位置を返す。見つからねば -1。

    Returns the starting position of the last match on the right side using regular expressions. Returns -1 if no match is found.
    
    ----------
    text : 
        Original text
    needle : 
        Target text
    from_pos : 
        Starting position
    include_current :
        Flag for including the outside of search range

    Returns
    -------
    out: 
        Start position searched using regular expressions to right direction from from_pos 
    """
    start = from_pos if include_current else from_pos + 1
    m = re.search(pattern, text[max(0, start):], flags)

    return (max(0, start) + m.start()) if m else -1

def get_np_histogram2d(
    data: list = None,
    bins: list = None,
    xrange: list = None,
    yrange: list = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    2Dヒストの生カウントとエッジを返す（plotly では z=counts.T を使う想定）

    Parameters
    ----------
    data : 
        2 or 3 dimansional data list [x[1,2,1,...,1], y[3,2,1,...,3], z[3,2,1,...,3]]
    bins : 
        bin information [bin number for x, bin number for y]
    xrange : 
        effective range for x axis [min, max]
    yrange : 
        effective range for y axis [min, max]

    Returns
    -------
    counts, xedges, yedges:
        Tuple returned values with `numpy.histogram2d`
    """
    if data is None:
        return None
    
    if xrange is None:
        xrange = []

    if yrange is None:
        yrange = []
    
    x = data[0]
    y = data[1]

    if len(data) == 2:

        x = pd.to_numeric(x, errors='coerce')
        y = pd.to_numeric(y, errors='coerce')

        mask = ~np.isnan(x) & ~np.isnan(y)
        x_clean = x[mask]
        y_clean = y[mask]

        if len(xrange) >= 2 and len(yrange) >= 2:
            counts, xedges, yedges = np.histogram2d(x_clean, y_clean, bins=bins,range=[xrange, yrange])
        else:
            counts, xedges, yedges = np.histogram2d(x_clean, y_clean, bins=bins) 

    else:

        def centers_to_edges_from_centers(centers: np.ndarray) -> np.ndarray:
            c = np.sort(np.unique(centers))       # ★ 重複除去が必須
            mid = 0.5 * (c[:-1] + c[1:])
            left  = c[0]  - (c[1]  - c[0])  / 2
            right = c[-1] + (c[-1] - c[-2]) / 2
            return np.r_[left, mid, right]
        
        w = data[2]

        xedges = centers_to_edges_from_centers(x)
        yedges = centers_to_edges_from_centers(y)

        counts, xedges, yedges = np.histogram2d(x, y, bins=[xedges, yedges], weights=w)

    return counts, xedges, yedges

def slice_1d_from_2dhist(
    counts: np.ndarray,
    xedges: np.ndarray,
    yedges: np.ndarray,
    bin_index: int,
    *,
    slice_axis: str = "x",
    bin_span: int = 1,
    normalize: bool = False,
) -> Dict[str, Any]:
    """
    二次元ヒスト (counts: shape=(nx, ny)) を、指定軸のビン範囲で合算し、
    残りの軸の 1D ヒストグラムを返す。あわせて**固定した軸側の中心値・ビン幅**も返す。

    Parameters
    ----------
    counts : np.ndarray, shape = (nx, ny)
    xedges : np.ndarray, shape = (nx+1,)
    yedges : np.ndarray, shape = (ny+1,)
    bin_index : int
        スライス開始ビン（0 始まり）
    slice_axis : {'x','y'}
        'x' → xビンを [bin_index, bin_index+bin_span) 固定して y 分布を返す  
        'y' → yビンを [bin_index, bin_index+bin_span) 固定して x 分布を返す
    bin_span : int, default 1
        何ビン分まとめるか（終了ビンは含まない）
    normalize : bool, default False
        True のとき 1D ヒストを総和 1 で正規化

    Returns
    -------
    dict
        {
          "counts":        np.ndarray  # 残り軸の 1D ヒスト（合算後）
          "edges":         np.ndarray  # 残り軸のエッジ (n_other+1,)
          "centers":       np.ndarray  # 残り軸の中心 (n_other,)
          "widths":        np.ndarray  # 残り軸のビン幅 (n_other,)
          "slice_axis":    str         # 'x' or 'y'
          "indices":       np.ndarray  # 固定した軸のビンインデックス [start..stop-1]
          "slice_edges":   np.ndarray  # 固定した軸の選択エッジ列 (bin_span+1,)
          "slice_centers": np.ndarray  # 固定した軸の選択ビン中心 (bin_span,)
          "slice_widths":  np.ndarray  # 固定した軸の選択ビン幅 (bin_span,)
          "bin_index":     int         # 
          "bin_span":      int         #
        }
    """
    if counts.ndim != 2:
        raise ValueError("counts must be 2D (nx, ny)")

    nx, ny = counts.shape
    if len(xedges) != nx + 1 or len(yedges) != ny + 1:
        raise ValueError("xedges/yedges shape mismatch with counts shape.")

    if slice_axis not in ("x", "y"):
        raise ValueError("slice_axis must be 'x' or 'y'")

    if bin_span < 1:
        raise ValueError(f"bin_span must be >= 1, got {bin_span}")

    if slice_axis == "x":
        start = bin_index
        stop  = bin_index + bin_span
        if not (0 <= start < nx) or not (start < stop <= nx):
            raise IndexError(f"x bin range out of range: start={start}, stop={stop}, nx={nx}")

        counts_1d = counts[start:stop, :].sum(axis=0).astype(float)
        other_edges   = yedges
        other_centers = 0.5 * (yedges[:-1] + yedges[1:])
        other_widths  = np.diff(yedges)

        slice_edges   = xedges[start:stop+1]
        slice_centers = 0.5 * (slice_edges[:-1] + slice_edges[1:])
        slice_widths  = np.diff(slice_edges)
        indices = np.arange(start, stop)

    else:  # slice_axis == "y"
        start = int(bin_index)
        stop  = start + int(bin_span)
        if not (0 <= start < ny) or not (start < stop <= ny):
            raise IndexError(f"y bin range out of range: start={start}, stop={stop}, ny={ny}")

        counts_1d = counts[:, start:stop].sum(axis=1).astype(float)
        other_edges   = xedges
        other_centers = 0.5 * (xedges[:-1] + xedges[1:])
        other_widths  = np.diff(xedges)

        slice_edges   = yedges[start:stop+1]
        slice_centers = 0.5 * (slice_edges[:-1] + slice_edges[1:])
        slice_widths  = np.diff(slice_edges)
        indices = np.arange(start, stop)

    if normalize and counts_1d.sum() > 0:
        counts_1d = counts_1d / counts_1d.sum()

    return {
        "counts":        counts_1d,
        "edges":         other_edges,
        "centers":       other_centers,
        "widths":        other_widths,
        "slice_axis":    slice_axis,
        "indices":       indices,
        "slice_edges":   slice_edges,
        "slice_centers": slice_centers,
        "slice_widths":  slice_widths,
        "bin_index":     start,
        "bin_span":      bin_span,
    }


def get_slice_array(
    data: list = None,
    bins: list = None, 
    xrange: list = None,
    yrange: list = None,
    slice_axis: str = "x", 
    bin_span: int = 1,
    normalize: bool = False,
    histo_skip: bool = False
) -> list:
    """
    二次元ヒストグラムから任意の便数でまとめた頻度を一次元ヒストグラムのリストとして取得する。

    Get a list of one-dimensional histograms representing counts sliced by any number of bins from a two-dimensional histogram.
        
    Parameters
    ----------
    data : 
        2 dimansional data list [x[1,2,1,...,1], y[3,2,1,...,3]]
    bins : 
        Bin information [bin number for x, bin number for y]
    xrange : 
        Effective range for x axis [min, max]
    yrange : 
        Effective range for y axis [min, max]
    slice_axis : 
        Axis label in string format 
    bin_span : 
        Number of bin to be grouped
    normalize : 
        Normarize option
    histo_skip : 
        Flag to skip numpy.histogram2d

    Returns
    -------
    histo_array: 
        List of one dimensional histogram information 
    """  
    histo_array = []
    data2d = get_np_histogram2d(data, bins, xrange, yrange) if histo_skip is False else data
    max_loop = len(data2d[0][0])//bin_span if slice_axis == 'y' else len(data2d[0])//bin_span

    for i in range(max_loop):
        bin_index = i * bin_span
        data1d = slice_1d_from_2dhist(
                *data2d, 
                bin_index=bin_index,
                slice_axis=slice_axis,
                bin_span=bin_span,
                normalize=normalize,
            )
        histo_array.append(data1d)

    return histo_array


def add_sub_plot(
    fig:go.Figure,
    irow:int = 1,
    icol:int = 1, 
    data:list | None = None,
    axes_title:list | None = None,
    log_option:str | list | None = None,
    legend_option:list | None = None,  
    func: Callable[..., Any] | None = None,
    **kwargs,
):
    """
    データを簡便に追加するための関数。

    Function for adding figure in plotly.graph_objects.Figure 

    Parameters
    ----------
    fig : 
        Instance of plotly.graph_objects.Figure 
    irow : 
        Row number
    icol : 
        Column number
    data : 
        Data list (format depends on func)
    axes_title : 
        Axis title list [x, y]
    log_option : 
        log option for x and y axis. 
        Input format is two characters. 
        If '00' -> x: liner, y: liner, if '10' ->  x: log, y: liner.
    legend_option : {x position, y posiyion, x anchor, y anchor, orientation, margin}
        0	legend.x: range is from 0.0 to 1.0
        1	legend.y: range is from 0.0 to 1.0
        2	legend.xanchor: "left", "center", "right"
        3	legend.yanchor: "top", "middle", "bottom"
        4	legend.orientation: "v" or "h"
        5	margin.r: pixcel（e.g.: 0, 40）
    func : 
        user defined function
        existed function list:
            go_Histogram
            go_Heatmap
            go_Scatter
            go_Bar
    **kwargs : 
        dictionary to store additional arguments for func
    """
    if axes_title is None:
        axes_title = ['x', 'y']

    if log_option is None:
        log_option = [False, False]

    else:
        logs = []
        
        for i in range(2):
            val_bool = True if log_option[i] == "1" else False
            logs.append(val_bool)

        log_option = logs

    xtype = '-' if log_option[0] is False else 'log'
    ytype = '-' if log_option[1] is False else 'log'

    if func is not None:
        sig = inspect.signature(func)
        accepted = {k: v for k, v in kwargs.items() if k in sig.parameters}
        func(fig, irow, icol, data, **accepted)

    fig.update_xaxes(
        type = xtype,
        title_text = axes_title[0],
        row = irow,
        col = icol
    )

    fig.update_yaxes(
        type = ytype,
        title_text = axes_title[1],
        row = irow,
        col = icol
    )

    if legend_option is not None:
        if len(legend_option) > 5:
            fig.update_layout(
                legend=dict(
                    x = legend_option[0],
                    y = legend_option[1],   
                    xanchor = legend_option[2],
                    yanchor = legend_option[3],
                    orientation = legend_option[4]  
                ),
                margin=dict(r = legend_option[5])               
        )


def go_Histogram(
    fig:go.Figure, 
    irow:int,
    icol:int,
    data:list,
    bins:list[int] | None = None,
    xrange:list[int,int] | None = None,
    dataname:str | None = None,
):
    """
    plotly.graph_objectsのHistogramを使って図を追加する関数

    Function to draw data using plotly.graph_objects.Histogram

    Parameters
    ----------
    fig : 
        Instance of plotly.graph_objects.Figure 
    irow : 
        Row number
    icol : 
        Column number
    data : 
        Data list (format depends on func)
    bins : 
        Bin number
    xrange : [min, max] 
        Valid range
    dataneme :
        Data object label name
    """
    bins = [200] if bins is None else bins

    if xrange is None:
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


def go_Heatmap(
    fig:go.Figure, 
    irow:int,
    icol:int,
    data:list,
    bins:list[int,int] | None = None,
    logz_option:bool = False,
    xrange:list[int,int] | None = None,
    yrange:list[int,int] | None = None,
    debug:bool = False,
    dataname:str | None = None,
    colormap:str = "Turbo"
):
    """
    plotly.graph_objectsのHistogramを使って図を追加する関数

    Function to draw data using plotly.graph_objects.Histogram

    Parameters
    ----------
    fig : 
        Instance of plotly.graph_objects.Figure 
    irow : 
        Row number
    icol : 
        Column number
    data : 
        Data list (format depends on func)
    bins : 
        Bin number
    logz_option : [min, max] 
        Log option for z axis
    xrange : [min, max] 
        Valid range for x direction
    yrange : [min, max] 
        Valid range for y direction
    debug :
        Debug flag
    dataname :
        Data object label name
    colormap :
        colomap name
    """
    bins = [200, 200] if bins is None else bins

    counts, xedges, yedges = get_np_histogram2d(data=data, bins=bins, xrange=xrange, yrange=yrange)
    
    if logz_option:
        counts = np.log10(counts + 1)

    bar_title = "ln(+1)" if logz_option else "Count" 

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


def go_Scatter(
    fig:go.Figure, 
    irow:int,
    icol:int,
    data:list,
    mode:str = 'markers',
    size:int = 4,
    width:int = 1,
    dataname:str | None = None,
    color:str | None = None,
    y_error:list | None = None,
    x_error:list | None = None,
    errors_type:str = 'data' 
):
    """
    plotly.graph_objectsのHistogramを使って図を追加する関数

    Function to draw data using plotly.graph_objects.Histogram

    Parameters
    ----------
    fig : 
        Instance of plotly.graph_objects.Figure 
    irow : 
        Row number
    icol : 
        Column number
    data : 
        Data list (format depends on func)
    mode
        Scatter polt option. 
        (e.g.) 'markers', 'lines', 'lines+markers' ...
    size :
        Scatter size
    width :
        Line width
    dataneme :
        Data object label name
    color
        Data color
    y_error :
        Error bar data for y axis
    x_error :
        Error bar data for x axis
    errors_type :
        Error plot option.
        (e.g.) 'data', 'percent'
    """
    if y_error is not None:
        if len(y_error) == 1:
            error_y = dict(
                type = errors_type,
                array = y_error[0],
                visible = True
            )
        elif len(y_error) >= 2:
            error_y = dict(
                type = errors_type,
                array = y_error[0],
                arrayminus = y_error[1],
                visible = True
            )
    else:
        error_y = None

    if x_error is not None:
        if len(x_error) == 1:
            error_x = dict(
                type = errors_type,
                array = x_error[0],
                visible = True
            )
        elif len(x_error) >= 2:
            error_x = dict(
                type = errors_type,
                array = x_error[0],
                arrayminus = x_error[1],
                visible = True
            )
    else:
        error_x = None

    if len(data) == 1:
        fig.add_trace(
            go.Scatter(
                y = data[0],
                mode =  mode,
                marker = dict(size = size, color = color),
                line = dict(width = width, color = color),
                name = dataname,
                error_y = error_y,
                error_x = error_x 
            ),
            row=irow, col=icol
        )
    else:
        fig.add_trace(
            go.Scatter(
                x = data[0],
                y = data[1],
                mode =  mode,
                marker = dict(size = size, color = color),
                line = dict(width = width, color = color),
                name = dataname,
                error_y = error_y,
                error_x = error_x 
            ),
            row=irow, col=icol
        )

def go_Bar(
    fig:go.Figure, 
    irow:int,
    icol:int,
    data:list,
    dataname:str | None = None,
):
    """
    plotly.graph_objectsのHistogramを使って図を追加する関数

    Function to draw data using plotly.graph_objects.Histogram

    Parameters
    ----------
    fig : 
        Instance of plotly.graph_objects.Figure 
    irow : 
        Row number
    icol : 
        Column number
    data : 
        Data list (format depends on func)
    dataneme :
        Data object label name
    """
    fig.add_trace(
        go.Bar(
            x = data[0],
            y = data[1],
            name = dataname,
        ),
        row = irow,
        col = icol
    )


def align_colorbar(fig, thickness=20, thicknessmode="pixels"):
    """
    二次元ヒストグラムのカラーバーを配置する

    Adjust the color bar positions for the two-dimensional histogram
        
    Parameters
    ----------
    fig : 
        Instance of plotly.graph_objects.Figure 
    thickness : 
        Color bar width
    thicknessmode : 
        Width unit
    """  
    for trace in fig.data:
        if isinstance(trace, go.Heatmap):
            xaxis = "xaxis" if trace.xaxis == "x" else "xaxis" + trace.xaxis[1:]
            yaxis = "yaxis" if trace.yaxis == "y" else "yaxis" + trace.yaxis[1:]

            xa = fig.layout[xaxis].domain
            ya = fig.layout[yaxis].domain

            trace.update(colorbar=dict(thickness=thickness, thicknessmode=thicknessmode, x=xa[1] + 0.01, y=(ya[0] + ya[1]) / 2, len=ya[1] - ya[0]))