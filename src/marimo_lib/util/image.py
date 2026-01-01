from __future__ import annotations
from pathlib import Path
import base64
from PIL import Image
import html
from typing import Literal, Optional, Union
import marimo as mo
import re 

from io import BytesIO
from urllib.parse import urlparse
from urllib.request import urlopen

PathOrStr = Union[str, Path]
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
    input_path: PathOrStr = "images.png",
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

    # -----------------------
    # 1) 入力をURL/Pathに分岐
    # -----------------------
    url: Optional[str] = None
    path: Optional[Path] = None

    if isinstance(input_path, Path):
        path = input_path
    elif isinstance(input_path, str):
        p = urlparse(input_path)
        if p.scheme in ("http", "https"):
            # 'https:/raw...' のような壊れたURLをここで弾く（// は勝手に直さない）
            if not p.netloc:
                raise ValueError(
                    f"URLが不正です: {input_path!r}\n"
                    f"'https://...' のようにスキームの後ろは '//' にしてください。"
                )
            url = input_path
        else:
            # 相対/絶対パスは Path へ（文字列の // はそのまま渡す）
            path = Path(input_path)
    else:
        raise TypeError(f"input_path must be str or Path, got {type(input_path)!r}")

    # -----------------------
    # 2) 画像の bytes と (w,h) を取得
    # -----------------------
    def _load_bytes_and_size_from_url(u: str) -> tuple[bytes, int, int]:
        data = urlopen(u).read()
        with Image.open(BytesIO(data)) as img:
            w, h = img.size
        return data, w, h

    def _load_bytes_and_size_from_path(p: Path) -> tuple[bytes, int, int]:
        if not p.is_file():
            raise FileNotFoundError(f"画像ファイルが見つかりません: {p}")
        data = p.read_bytes()
        with Image.open(BytesIO(data)) as img:
            w, h = img.size
        return data, w, h

    if url is not None:
        data, img_w, img_h = _load_bytes_and_size_from_url(url)
    else:
        assert path is not None
        data, img_w, img_h = _load_bytes_and_size_from_path(path)

    # -----------------------
    # 3) 幅・高さの自動計算（px指定のときだけ）
    # -----------------------
    w_px = _parse_px(width)
    h_px = _parse_px(height)

    computed_width: Optional[SizeLike] = width
    computed_height: Optional[SizeLike] = height

    if width is not None and height is None and w_px is not None:
        computed_height = int(round(w_px * (img_h / img_w)))
    elif height is not None and width is None and h_px is not None:
        computed_width = int(round(h_px * (img_w / img_h)))

    alt_escaped = html.escape(alt_name)

    # -----------------------
    # 4) mode ごとの return（形式は変えない）
    # -----------------------
    if mode == "data_url":
        b64 = base64.b64encode(data).decode("ascii")

        style_parts = ["max-width:none"]
        # 高さを指定していない場合のみ height:auto
        if computed_height is None:
            style_parts.append("height:auto")

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
        return mo.Html(html_text)

    if mode == "file_src":
        # URL ならブラウザが直接取れるので <img src="..."> でOK
        if url is not None:
            style_parts = ["max-width:none"]
            if computed_height is None:
                style_parts.append("height:auto")
            if computed_width is not None:
                style_parts.append(f"width:{_to_css_size(computed_width)}")
            if computed_height is not None:
                style_parts.append(f"height:{_to_css_size(computed_height)}")
            if rounded:
                style_parts.append(f"border-radius:{round_radius}")
                style_parts.append("overflow:hidden")

            style_attr = "; ".join(style_parts)

            html_text = (
                f'<img src="{html.escape(url)}" '
                f'alt="{alt_escaped}" '
                f'style="{style_attr}" />'
            )
            return mo.Html(html_text)

        # Path はブラウザが直接読めないので mo.image に任せる
        assert path is not None
        inner = mo.image(src=path, rounded=False)  # marimo に配信/埋め込みをやらせる
        img_html = inner.text

        # ここで「勝手に 100% 幅になる」系を上書きする
        style_parts = ["max-width:none", "width:auto", "height:auto", "display:inline-block"]
        if computed_width is not None:
            style_parts.append(f"width:{_to_css_size(computed_width)}")
        if computed_height is not None:
            style_parts.append(f"height:{_to_css_size(computed_height)}")
        if rounded:
            style_parts.append(f"border-radius:{round_radius}")

        inject = "; ".join(style_parts)

        # 既に style がある場合は追記、無ければ追加
        if ' style="' in img_html:
            img_html = re.sub(r'style="', f'style="{inject}; ', img_html, count=1)
        else:
            img_html = img_html.replace("<img ", f'<img style="{inject}" ', 1)

        return mo.Html(img_html)


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