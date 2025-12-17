import plotly
import plotly.express as px
import pandas as pd
import datetime as dt
import plotly.graph_objects as go
from typing import Any
import os 

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
            f"rgba(255, 179, 186, {alpha})",
            f"rgba(255, 223, 186, {alpha})",
            f"rgba(255, 255, 186, {alpha})",
            f"rgba(186, 255, 201, {alpha})",
            f"rgba(186, 225, 255, {alpha})", 
        ]

    elif label == "neon":
        color_list = [
            f"rgba( 57, 255,  20, {alpha})",
            f"rgba(255,  20, 147, {alpha})",
            f"rgba(  0, 255, 255, {alpha})",
            f"rgba(255, 255,   0, {alpha})",
            f"rgba(138,  43, 226, {alpha})",
        ]

    elif label == "tab10":
        color_list = [
            f"rgba( 31, 119, 180, {alpha})",
            f"rgba(255, 127,  14, {alpha})",
            f"rgba( 44, 160,  44, {alpha})",
            f"rgba(214,  39,  40, {alpha})",
            f"rgba(148, 103, 189, {alpha})",
            f"rgba(140,  86,  75, {alpha})",
            f"rgba(227, 119, 194, {alpha})",
            f"rgba(127, 127, 127, {alpha})",
            f"rgba(188, 189,  34, {alpha})",
            f"rgba( 23, 190, 207, {alpha})",
        ]

    elif label == "ud":
        color_list = [
            f"rgba(  0,   0,   0, {alpha})",
            f"rgba(230, 159,   0, {alpha})",
            f"rgba( 86, 180, 233, {alpha})",
            f"rgba(  0, 158, 115, {alpha})",
            f"rgba(240, 228,  66, {alpha})",
            f"rgba(  0, 114, 178, {alpha})",
            f"rgba(213,  94,   0, {alpha})",
            f"rgba(204, 121, 167, {alpha})",
        ]

    return color_list


def init_schedule():
    return pd.DataFrame(columns=["task", "start", "end", "resource", "name"])


def add_periodic_task(
    data: pd.DataFrame | None,
    *,
    task: str,
    start: str, 
    end: str,
    resource: str,
    name: str,
    repeat_until: str,
    every: int = 1,
    unit: str = "D",
    seq_col: str | None = "Seq",
    **extra_cols: Any,
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
            unit="D",
            seq_col="MeetingID",
            Room="会議室A",
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
            "task": task,
            "start": st.strftime("%Y-%m-%d %H:%M"),
            "end":   ed.strftime("%Y-%m-%d %H:%M"),
            "resource": resource,
            "name": name,
        }

        if seq_col is not None:
            row_kwargs[seq_col] = i

        row_kwargs.update(extra_cols)

        add_task(data=data, **row_kwargs,)


def add_task(
    data: pd.DataFrame | None = None,
    *,
    task: str = "Task1",
    start: str = "2025-11-10 0:00",
    end:   str = "2025-11-10 23:59",
    resource: str = "Resource1",
    name: str = "Name1",
    **extra_cols: Any,
) -> pd.DataFrame:
    """
    1件のタスク行を DataFrame に追加する。
    ユーザーは任意の追加カラムを keyword 引数で渡せる。

    例:
        df = add_task(
            None,
            task="Job A",
            atart="2025-11-10 09:00",
            end="2025-11-10 17:00",
            resource="Alex",
            name="Test1",
            priority=1,
            memo="first job",
        )
    """

    new_row: dict[str, Any] = {
        "task": task,
        "start": start,
        "end": end,
        "resource": resource,
        "name": name,
    }

    new_row.update(extra_cols)

    if data is None:
        data = pd.DataFrame([new_row])
    else:
        data.loc[len(data)] = new_row


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
        tickformat="%m/%d(%a)\n%H:%M",
        ticklabelmode="period",
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


def load_schedule_file_as_str(input_path:str =  "filepath") -> str:
    """
    ファイルを読み込む関数

    Load file.

    Parameters
    ----------
    input_path : 
        Input file path 

    Returns
    -------
    str: 
        String型に格納されたテキスト
    """
    if os.path.isfile(input_path) is True:
        with open(input_path, "r", encoding="utf-8") as f:
            txt = f.read()

        return txt
    
    else:
        return ""
    

def parse_schedule_txt(txt:str | None = None) -> list[dict[any, any]]:
    if txt is not None:
        lines = txt.strip().splitlines()
        header = lines[0].split(",")
        rows = []

        for line in lines[1:]:
            if not line.strip():
                continue

            fields = line.split(",")
            row_dict = dict(zip(header, fields))
            rows.append(row_dict)
        
        return rows

    else:
        return None


def add_task_csv(
    data: pd.DataFrame | None = None,
    input_path: str | None = None,
    func_label: str = "func",
) -> pd.DataFrame:
    
    csv_str = load_schedule_file_as_str(input_path)
    csv_list = parse_schedule_txt(csv_str)

    for row in csv_list:
        func_name = row.get(func_label, "").strip()

        if not func_name:
            continue

        kwargs: dict[str, Any] = {
            k: v for k, v in row.items()
            if k != func_label and v != ""
        }

        if "every" in kwargs:
            kwargs["every"] = int(kwargs["every"])
        if "priority" in kwargs:
            kwargs["priority"] = int(kwargs["priority"])

        if func_name == "add_task":
            add_task(data=data, **kwargs,)

        elif func_name == "add_periodic_task":
            add_periodic_task(data=data, **kwargs,)

        else:
            print(f"unknown func: {func_name}, row={row}")
            continue