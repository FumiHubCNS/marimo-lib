from pathlib import Path
import base64

def get_image_html(
    input_path:str = 'images.png',
    alt_name:str = 'サンプル画像'
):
    path = Path("")

    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")

    html = f'<img src="data:image/png;base64,{b64}" alt="{alt_name}" />'

    return html