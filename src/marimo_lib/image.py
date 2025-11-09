from pathlib import Path
import base64
from PIL import Image

def get_image_html(
    input_path: str = "images.png",
    alt_name: str = "サンプル画像",
) -> str:
    path = Path(input_path)

    if not path.is_file():
        raise FileNotFoundError(f"画像ファイルが見つかりません: {path}")

    with Image.open(path) as img:
        width, height = img.size

    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")

    html = (
        f'<img src="data:image/png;base64,{b64}" '
        f'alt="{alt_name}" '
        f'width="{width}" height="{height}" '
        f'style="max-width:none; height:auto;" />'
    )

    return html