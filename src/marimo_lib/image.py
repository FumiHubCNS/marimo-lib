from pathlib import Path
import base64
from PIL import Image
import html
from typing import Literal, Optional

def get_image_html(
    input_path: str = "images.png",
    alt_name: str = "サンプル画像",
    *,
    mode: Literal["data_url", "file_src"] = "data_url",
    width: Optional[str] = None,   # 例: "550px", "50%", None
    rounded: bool = False,
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
    src_escaped = html.escape(str(path))

    if mode == "data_url":
        data = path.read_bytes()
        b64 = base64.b64encode(data).decode("ascii")

        style_parts = ["max-width:none", "height:auto"]
        if width is not None:
            style_parts.append(f"width:{width}")
        if rounded:
            style_parts.append("border-radius:9999px")  # ほぼ丸 / pill 形

        style_attr = "; ".join(style_parts)

        html_text = (
            f'<img src="data:image/png;base64,{b64}" '
            f'alt="{alt_escaped}" '
            f'width="{img_width}" height="{img_height}" '
            f'style="{style_attr}" />'
        )
        return html_text

    if mode == "file_src":
        effective_width = width or f"{img_width}px"

        style_parts = [
            f"width:{effective_width}",
            "max-width:100%",   
            "height:auto",
            "display:block",
        ]
        if rounded:
            style_parts.append("border-radius:9999px")  

        style_attr = "; ".join(style_parts)

        html_text = (
            f'<img src="{src_escaped}" '
            f'alt="{alt_escaped}" '
            f'style="{style_attr}" />'
        )
        return html_text

    raise ValueError(f"未知の mode: {mode!r}")
