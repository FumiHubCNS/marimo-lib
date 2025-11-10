from __future__ import annotations
import anywidget
import traitlets
from pathlib import Path
from typing import Any, Dict
import json

class ExcalidrawWidget(anywidget.AnyWidget):
    """
    Excalidraw を iframe で marimo / Jupyter 上に埋め込むシンプル版。

    - width, height: ウィジェットのサイズ（px）
    - url: iframe で開く URL（デフォルトは https://excalidraw.com/）
    - scene: Excalidraw の JSON 文字列（Python から読み書きする用）

    注意:
        iframe 先が https://excalidraw.com/ のような別オリジンの場合、
        scene を直接 iframe の中に適用することはブラウザの制限でできません。
        ここでは「Python 側で JSON を読み書きして持っておく」用途を想定しています。
    """

    # この JS がブラウザ側で実行される
    _esm = Path(__file__).parent.parent / "static" / "excali.js"

    # _css = Path(__file__).parent / "static" / "excalidraw.min.css"

    # Python ↔ JS 同期する trait
    width: int = traitlets.Int(900).tag(sync=True)
    height: int = traitlets.Int(600).tag(sync=True)
    url: str = traitlets.Unicode("https://excalidraw.com/").tag(sync=True)

    # ★ Excalidraw の scene(JSON) を保持する trait（今は UI とは連動してない）
    scene: str = traitlets.Unicode("").tag(sync=True)

    def __init__(
        self,
        width: int = 900,
        height: int = 600,
        url: str = "https://excalidraw.com/",
        initial_scene: Dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(width=width, height=height, url=url, **kwargs)

        if initial_scene is not None:
            self.scene = json.dumps(initial_scene, ensure_ascii=False)

    def get_scene_dict(self) -> Dict[str, Any]:
        """
        現在の scene(JSON文字列) を Python の dict として返す。
        scene が空 or 壊れていれば空 dict を返す。
        """
        if not self.scene:
            return {}
        try:
            return json.loads(self.scene)
        except json.JSONDecodeError:
            return {}

    def set_scene_dict(self, data: Dict[str, Any]) -> None:
        """
        Python の dict を受け取り、scene(JSON文字列) に反映する。
        """
        self.scene = json.dumps(data, ensure_ascii=False)

    def load_scene_file(self, path: str | Path) -> None:
        """
        Excalidraw からエクスポートした JSON ファイルを読み込み、
        その中身を scene にセットする。

        例:
            w.load_scene_file("my_drawing.excalidraw")
        """
        path = Path(path)
        txt = path.read_text(encoding="utf-8")
        self.scene = txt

    def save_scene_file(self, path: str | Path) -> None:
        """
        現在の scene(JSON文字列) をファイルに保存する。

        例:
            w.save_scene_file("backup_scene.json")
        """
        path = Path(path)
        path.write_text(self.scene, encoding="utf-8")