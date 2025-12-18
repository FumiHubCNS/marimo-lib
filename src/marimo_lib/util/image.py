from __future__ import annotations
from pathlib import Path
import base64
from PIL import Image
import html
from typing import Literal, Optional, Union
import marimo as mo

SizeLike = Union[int, float, str]

def _parse_px(v: Optional[SizeLike]) -> Optional[float]:
    """int/float -> px とみなす。'123px' -> 123。'40%' 等は None."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().lower()
    if s.endswith("px"):
        try:
            return float(s[:-2].strip())
        except ValueError:
            return None
    # ％やemなどは計算できない
    return None

def _to_css_size(v: SizeLike) -> str:
    """int/float は px にする。str はそのまま."""
    if isinstance(v, (int, float)):
        return f"{v}px"
    return str(v)

def get_image_html(
    input_path: str = "images.png",
    alt_name: str = "サンプル画像",
    *,
    mode: Literal["data_url", "file_src"] = "data_url",
    width: Optional[SizeLike] = None,
    height: Optional[SizeLike] = None,
    rounded: bool = False,
    round_radius: str = "10%",
) -> str:
    """
    mode="data_url"  : <img src="data:image/png;base64,..."> を返す（従来どおり）
    mode="file_src"  : <img src="notebook/image/mini001.png" ...> を返す（mo.image 風）
    - width & height 両方指定: そのまま使う（縦横比は無視）
    - 片方だけ指定: もう片方は元画像の縦横比から自動計算（px指定のときのみ）
    - 未指定: 元サイズ
    """
    path = Path(input_path)
    
    if not path.is_file():
        raise FileNotFoundError(f"画像ファイルが見つかりません: {path}")

    with Image.open(path) as img:
        img_w, img_h = img.size

    w_px = _parse_px(width)
    h_px = _parse_px(height)

    computed_width: Optional[SizeLike] = width
    computed_height: Optional[SizeLike] = height

    if width is not None and height is None and w_px is not None:
        computed_height = int(round(w_px * (img_h / img_w)))

    elif height is not None and width is None and h_px is not None:
        computed_width = int(round(h_px * (img_w / img_h)))

    alt_escaped = html.escape(alt_name)

    if mode == "data_url":
        data = path.read_bytes()
        b64 = base64.b64encode(data).decode("ascii")

        style_parts = ["max-width:none", "height:auto"]
        if computed_width is not None:
            style_parts.append(f"width:{_to_css_size(computed_width)}")
        if computed_height is not None:
            style_parts.append(f"height:{_to_css_size(computed_height)}")
        if rounded:
            style_parts.append(f"border-radius:{round_radius}")

        style_attr = "; ".join(style_parts)

        w_attr = img_w
        h_attr = img_h
        if _parse_px(computed_width) is not None:
            w_attr = int(round(_parse_px(computed_width)))
        if _parse_px(computed_height) is not None:
            h_attr = int(round(_parse_px(computed_height))) 

        html_text = (
            f'<img src="data:image/png;base64,{b64}" '
            f'alt="{alt_escaped}" '
            f'width="{w_attr}" height="{h_attr}" '
            f'style="{style_attr}" />'
        )
        return html_text

    if mode == "file_src":
        if computed_height is None:
            return mo.image(src=path, width=computed_width, rounded=rounded)

        style = []
        if computed_width is not None:
            style.append(f"width:{_to_css_size(computed_width)}")
        if computed_height is not None:
            style.append(f"height:{_to_css_size(computed_height)}")
        if rounded:
            style.append(f"border-radius:{round_radius}; overflow:hidden")
        style_attr = "; ".join(style)

        inner = mo.image(src=path, rounded=False)
        return mo.Html(f'<div style="{style_attr}">{inner.text}</div>')

    raise ValueError(f"未知の mode: {mode!r}")

def get_video_html(
    input_path: str,
    *,
    width: Optional[str] = None,       
    controls: bool = True,
    autoplay: bool = False,
    loop: bool = False,
    muted: bool = False,
    mode: Literal["data_url", "file_src"] = "data_url",
) -> str:
    """
    動画ファイルから <video> タグのHTMLを生成する。

    mode="data_url" : <source src="data:video/mp4;base64,...">（HTML単体で完結）
    mode="file_src" : <source src="notebook/.../xxx.mp4">（通常のファイル参照）
    """
    path = Path(input_path)

    if not path.is_file():
        raise FileNotFoundError(f"動画ファイルが見つかりません: {path}")

    src_attr: str

    if mode == "data_url":
        # 動画ファイルを base64 にして data URL にする
        data = path.read_bytes()
        b64 = base64.b64encode(data).decode("ascii")
        # mp4 前提。必要なら拡張子で切り替えてもOK
        src_attr = f"data:video/mp4;base64,{b64}"
    elif mode == "file_src":
        # パスをそのまま src として使う
        src_attr = html.escape(str(path))
    else:
        raise ValueError(f"未知の mode: {mode!r}")

    # 属性を組み立て
    attr_list = []

    if controls:
        attr_list.append("controls")
    if autoplay:
        attr_list.append("autoplay")
    if loop:
        attr_list.append("loop")
    if muted:
        attr_list.append("muted")

    style_parts = ["max-width:100%", "height:auto"]
    if width is not None:
        style_parts.append(f"width:{width}")
    style_attr = "; ".join(style_parts)

    attrs = " ".join(attr_list)

    html_text = (
        f'<video {attrs} style="{style_attr}">'
        f'<source src="{src_attr}" type="video/mp4" />'
        "お使いのブラウザは video タグをサポートしていません。"
        "</video>"
    )
    return html_text


def get_plotly_iframe_html(
    html_text: str,
    *,
    width: str = "1290px",
    height: str = "515px",
    mode: Literal["srcdoc", "data_url"] = "data_url",
) -> str:
    """
    Plotly が埋め込まれた HTML 文字列を <iframe> に包んで返す。

    mode="data_url":
        <iframe src="data:text/html;base64,..."> 形式。
        生成された HTML ファイル 1 個で完結させたい場合に使う。

    mode="srcdoc":
        <iframe srcdoc="..."> 形式。
        こちらも外部ファイルには依存しないが、
        HTML 内にエスケープした中身を直接埋め込む。
    """

    if mode == "data_url":
        # HTML 全体を base64 にして data URL にする
        b64 = base64.b64encode(html_text.encode("utf-8")).decode("ascii")
        src = f"data:text/html;base64,{b64}"
        iframe = (
            f'<iframe src="{src}" '
            f'width="{width}" height="{height}" '
            f'style="border:none;"></iframe>'
        )
        return iframe

    elif mode == "srcdoc":
        # srcdoc 用に HTML を属性値としてエスケープ
        srcdoc = html.escape(html_text, quote=True)
        iframe = (
            f'<iframe srcdoc="{srcdoc}" '
            f'width="{width}" height="{height}" '
            f'style="border:none;"></iframe>'
        )
        return iframe

    else:
        raise ValueError(f"未知の mode: {mode!r}")