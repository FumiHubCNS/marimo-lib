from pathlib import Path
import base64
from PIL import Image
import html
from typing import Literal, Optional
import marimo as mo

def get_image_html(
    input_path: str = "images.png",
    alt_name: str = "サンプル画像",
    *,
    mode: Literal["data_url", "file_src"] = "data_url",
    width: Optional[str] = None,
    rounded: bool = False,
    round_radius: Optional[str] = '10%',  
) -> str:
    """
    mode="data_url"  : <img src="data:image/png;base64,..."> を返す（従来どおり）
    mode="file_src"  : <img src="notebook/image/mini001.png" ...> を返す（mo.image 風）
    """
    path = Path(input_path)

    if not path.is_file():
        raise FileNotFoundError(f"画像ファイルが見つかりません: {path}")

    with Image.open(path) as img:
        img_width, img_height = img.size

    alt_escaped = html.escape(alt_name)

    if mode == "data_url":
        data = path.read_bytes()
        b64 = base64.b64encode(data).decode("ascii")

        style_parts = ["max-width:none", "height:auto"]
        if width is not None:
            style_parts.append(f"width:{width}")
        if rounded:
            style_parts.append(f"border-radius:{round_radius}")  # ほぼ丸 / pill 形

        style_attr = "; ".join(style_parts)

        html_text = (
            f'<img src="data:image/png;base64,{b64}" '
            f'alt="{alt_escaped}" '
            f'width="{img_width}" height="{img_height}" '
            f'style="{style_attr}" />'
        )
        return html_text

    if mode == "file_src":
        return mo.image(src=path, width=img_width, rounded=rounded)

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