// static/excali.js
// React も CDN も使わず、ただ iframe で Excalidraw を開くだけの anywidget。

/**
 * anywidget が呼び出すエントリポイント
 *
 * @param {{ model: any, el: HTMLElement }} params
 */
function render({ model, el }) {
  // Python 側から同期されてくる値
  const width = model.get("width") ?? 900;
  const height = model.get("height") ?? 600;
  const url = model.get("url") ?? "https://excalidraw.com/";

  // コンテナを作り直す
  const container = document.createElement("div");
  container.style.width = width + "px";
  container.style.height = height + "px";
  container.style.border = "1px solid #888";
  container.style.boxSizing = "border-box";
  container.style.display = "flex";
  container.style.flexDirection = "column";

  // 上に簡単なヘッダ
  const header = document.createElement("div");
  header.style.flex = "0 0 auto";
  header.style.padding = "4px 8px";
  header.style.fontSize = "12px";
  header.style.background = "#f0f0f0";
  header.style.borderBottom = "1px solid #ccc";
  header.textContent = `Excalidraw iframe (url=${url})`;
  container.appendChild(header);

  // iframe 本体
  const iframe = document.createElement("iframe");
  iframe.src = url;
  iframe.style.flex = "1 1 auto";
  iframe.style.width = "100%";
  iframe.style.height = "100%";
  iframe.style.border = "none";
  iframe.setAttribute("loading", "lazy");

  container.appendChild(iframe);

  // DOM を差し替え
  el.replaceChildren(container);

  // Python 側で width/height/url が変わったときにサイズやURLを更新したいならここで監視
  model.on("change:width", () => {
    const w = model.get("width") ?? 900;
    container.style.width = w + "px";
  });

  model.on("change:height", () => {
    const h = model.get("height") ?? 600;
    container.style.height = h + "px";
  });

  model.on("change:url", () => {
    const newUrl = model.get("url") ?? "https://excalidraw.com/";
    iframe.src = newUrl;
    header.textContent = `Excalidraw iframe (url=${newUrl})`;
  });
}

// anywidget が期待する形：default export に { render } を出す
export default { render };
