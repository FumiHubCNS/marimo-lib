import plotly
import plotly.express as px
import pandas as pd
import datetime as dt
import plotly.graph_objects as go
from typing import Any

def get_color_list(label: str = "tokyo", alpha: float = 0.6):
    color_list = []

    if label == "tokyo":
        color_list = [
            f"rgba(255,  40,   0, {alpha})",
            f"rgba(250, 245,   0, {alpha})",
            f"rgba( 53, 161, 107, {alpha})",
            f"rgba(  0,  65, 255, {alpha})",
            f"rgba(102, 204, 255, {alpha})",
            f"rgba(255, 153, 160, {alpha})",
            f"rgba(255, 153,   0, {alpha})",
            f"rgba(154,   0, 121, {alpha})",
            f"rgba(102,  51,   0, {alpha})",
        ]

    elif label == "facebook":
        color_list = [
            f"rgba( 76, 100,  21, {alpha})",
            f"rgba(207,  46, 146, {alpha})",
            f"rgba(242, 105,  57, {alpha})",
            f"rgba(255, 221, 131, {alpha})",
        ]

    elif label == "google":
        color_list = [
            f"rgba( 66, 133, 244, {alpha})",
            f"rgba( 15, 158,  88, {alpha})",
            f"rgba( 24, 180,   0, {alpha})",
            f"rgba(219,  68,  55, {alpha})",
        ]

    elif label == "pastel":
        color_list = [
            f"rgba(255, 179, 186, {alpha})",  # ピンク
            f"rgba(255, 223, 186, {alpha})",  # オレンジ
            f"rgba(255, 255, 186, {alpha})",  # イエロー
            f"rgba(186, 255, 201, {alpha})",  # グリーン
            f"rgba(186, 225, 255, {alpha})",  # ブルー
        ]

    elif label == "neon":
        color_list = [
            f"rgba( 57, 255,  20, {alpha})",  # ネオングリーン
            f"rgba(255,  20, 147, {alpha})",  # ディープピンク
            f"rgba(  0, 255, 255, {alpha})",  # シアン
            f"rgba(255, 255,   0, {alpha})",  # イエロー
            f"rgba(138,  43, 226, {alpha})",  # ブルーバイオレット
        ]

    elif label == "tab10":
        color_list = [
            f"rgba( 31, 119, 180, {alpha})",  # 青
            f"rgba(255, 127,  14, {alpha})",  # オレンジ
            f"rgba( 44, 160,  44, {alpha})",  # 緑
            f"rgba(214,  39,  40, {alpha})",  # 赤
            f"rgba(148, 103, 189, {alpha})",  # 紫
            f"rgba(140,  86,  75, {alpha})",  # 茶
            f"rgba(227, 119, 194, {alpha})",  # ピンク
            f"rgba(127, 127, 127, {alpha})",  # グレー
            f"rgba(188, 189,  34, {alpha})",  # 黄緑
            f"rgba( 23, 190, 207, {alpha})",  # 水色
        ]

    elif label == "ud":
        color_list = [
            f"rgba(  0,   0,   0, {alpha})",  # 黒
            f"rgba(230, 159,   0, {alpha})",  # オレンジ
            f"rgba( 86, 180, 233, {alpha})",  # スカイブルー
            f"rgba(  0, 158, 115, {alpha})",  # 青緑
            f"rgba(240, 228,  66, {alpha})",  # 黄
            f"rgba(  0, 114, 178, {alpha})",  # 青
            f"rgba(213,  94,   0, {alpha})",  # バーミリオン
            f"rgba(204, 121, 167, {alpha})",  # 赤紫
        ]

    return color_list


def add_periodic_task(
    data: pd.DataFrame | None,
    *,
    task: str,
    start: str,          # 1回目の開始日時 "2025-11-05 13:30" など
    end: str,            # 1回目の終了日時 "2025-11-05 14:00" など
    resource: str,
    name: str,
    repeat_until: str,   # どこまで繰り返すか（開始時刻がこの日時を超えない範囲）
    every: int = 1,      # 何単位ごとに繰り返すか
    unit: str = "D",     # "D"=日, "H"=時間, "W"=週 など pandas の freq 文字
    seq_col: str | None = "Seq",  # 連番カラム名（Noneなら作らない）
    **extra_cols: Any,   # 任意の追加カラム
) -> pd.DataFrame:
    """
    周期的にイベントを追加する。

    例:
        add_periodic_task(
            data=df,
            task="打ち合わせ",
            start="2025-11-05 13:30",
            end="2025-11-05 14:00",
            resource="Event",
            name="打ち合わせ①",
            repeat_until="2025-11-30 23:59",
            every=7,
            unit="D",  # 7日ごと（=毎週）
            seq_col="MeetingID",
            Room="会議室A",    # extra_cols の例
        )
    """

    start0 = pd.to_datetime(start)
    end0   = pd.to_datetime(end)
    duration = end0 - start0

    if every <= 0:
        raise ValueError("every は 1 以上の整数にしてください。")

    freq = f"{every}{unit}"

    limit = pd.to_datetime(repeat_until)

    start_times = pd.date_range(start=start0, end=limit, freq=freq)

    for i, st in enumerate(start_times, start=1):
        ed = st + duration

        row_kwargs: dict[str, Any] = {
            "Task": task,
            "Start": st.strftime("%Y-%m-%d %H:%M"),
            "End":   ed.strftime("%Y-%m-%d %H:%M"),
            "Resource": resource,
            "Name": name,
        }

        if seq_col is not None:
            row_kwargs[seq_col] = i

        row_kwargs.update(extra_cols)

        data = add_task(
            data=data,
            **row_kwargs,
        )

    return data

def add_task(
    data: pd.DataFrame | None = None,
    *,
    Task: str = "Task1",
    Start: str = "2025-11-10 0:00",
    End:   str = "2025-11-10 23:59",
    Resource: str = "Resource1",
    Name: str = "Name1",
    **extra_cols: Any,
) -> pd.DataFrame:
    """
    1件のタスク行を DataFrame に追加する。
    ユーザーは任意の追加カラムを keyword 引数で渡せる。

    例:
        df = add_task(
            None,
            Task="Job A",
            Start="2025-11-10 09:00",
            End="2025-11-10 17:00",
            Resource="Alex",
            Name="Test1",
            Priority=1,
            Memo="first job",
        )
    """

    new_row: dict[str, Any] = {
        "Task": Task,
        "Start": Start,
        "End": End,
        "Resource": Resource,
        "Name": Name,
    }

    new_row.update(extra_cols)

    if data is None:
        data = pd.DataFrame([new_row])
    else:
        data.loc[len(data)] = new_row

    return data


def add_schedule(
    fig: plotly.graph_objects.Figure | None = None,
    data: pd.DataFrame | None = None,
    timeline_info: dict[str, str] | None = None,
    color_discrete_map: dict[str, str] | None = None,
    edge_color_map: dict[str, str] | None = None,
    taskname_info: dict | None = None,
    line_info: dict | None = None,
    ref_time:dt.datetime = dt.datetime.now(),
    irow: int = 1,
    icol: int = 1,
):

    if fig is None:
        fig = go.Figure()

    if data is None:
        raise ValueError("data (DataFrame) must be provided.")

    if timeline_info is None:
        raise ValueError("timeline_info must be provided.")

    if color_discrete_map is not None and not isinstance(color_discrete_map, dict):
        color_discrete_map = dict(color_discrete_map)

    if edge_color_map is None:
        edge_color_map = {}
    elif not isinstance(edge_color_map, dict):
        edge_color_map = dict(edge_color_map)

    if taskname_info is None:
        taskname_info = dict(size=14, color="white")

    if line_info is None:
        line_info = dict(color="red", width=2, dash="dot")

    px_fig = px.timeline(
        data,
        x_start=timeline_info["x_start"],
        x_end=timeline_info["x_end"],
        y=timeline_info["y"],
        color=timeline_info["color"],
        text=timeline_info["text"],
        color_discrete_map=color_discrete_map,
    )

    px_fig.for_each_trace(
        lambda tr: tr.update(
            marker_line_color=edge_color_map.get(tr.name, "black"),
            marker_line_width=1,
            opacity=0.6,
            textposition="inside",
            insidetextanchor="middle",
            textfont=taskname_info,
        )
    )

    for tr in px_fig.data:
        fig.add_trace(tr, row=irow, col=icol)

    fig.update_xaxes(
        type="date",
        showgrid=True,
        gridwidth=1,
        griddash="dot",
        row=irow,
        col=icol,
    )

    fig.add_vline(
        x=ref_time,
        line=line_info,
        row=irow,
        col=icol,
    )

    fig.update_layout(
        barmode="overlay",
        showlegend=False,
    )