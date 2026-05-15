#!/usr/bin/env python3
import argparse
import html
import json
from pathlib import Path


def load_records(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def build_html(records: list[dict], title: str, per_page: int) -> str:
    escaped_title = html.escape(title)
    data = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f5f0;
      --ink: #1f2326;
      --muted: #666d70;
      --panel: #ffffff;
      --soft-panel: #fbfaf7;
      --line: #dfd9cf;
      --accent: #2e6f73;
      --accent-dark: #22595c;
      --error: #a13a32;
      --shadow: 0 14px 34px rgba(31, 35, 38, 0.1);
      --cols: 5;
      --thumb: 360px;
      --gap: 14px;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}

    header {{
      position: sticky;
      top: 0;
      z-index: 10;
      background: rgba(247, 245, 240, 0.95);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(12px);
    }}

    .bar {{
      max-width: 1480px;
      margin: 0 auto;
      padding: 18px 20px;
      display: grid;
      gap: 14px;
    }}

    .top {{
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 18px;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(24px, 3vw, 36px);
      line-height: 1.05;
      letter-spacing: 0;
    }}

    .summary {{
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 14px;
    }}

    .pager,
    .controls {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }}

    button {{
      min-height: 36px;
      padding: 0 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      color: var(--ink);
      font: inherit;
      cursor: pointer;
      transition: border-color 120ms ease, background 120ms ease, color 120ms ease, transform 120ms ease;
    }}

    button:hover:not(:disabled) {{
      border-color: var(--accent);
      color: var(--accent);
    }}

    button:disabled {{
      opacity: 0.45;
      cursor: not-allowed;
    }}

    .page-number.active {{
      background: var(--ink);
      color: #fff;
      border-color: var(--ink);
    }}

    .readout {{
      color: var(--muted);
      font-size: 14px;
      min-width: 158px;
    }}

    .control {{
      min-height: 36px;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      color: var(--muted);
      font-size: 13px;
      box-shadow: 0 6px 18px rgba(31, 35, 38, 0.05);
    }}

    input[type="range"] {{
      width: 112px;
      accent-color: var(--accent);
    }}

    output {{
      color: var(--ink);
      font-weight: 720;
      min-width: 30px;
      text-align: right;
    }}

    main {{
      max-width: 1480px;
      margin: 0 auto;
      padding: 20px;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(var(--cols), minmax(0, 1fr));
      gap: var(--gap);
    }}

    .card {{
      position: relative;
      min-width: 0;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: visible;
      box-shadow: 0 8px 22px rgba(31, 35, 38, 0.07);
      transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
    }}

    .thumb {{
      height: var(--thumb);
      overflow: hidden;
      background: #e8e2d8;
      border-radius: 7px 7px 0 0;
      cursor: pointer;
      border-bottom: 1px solid var(--line);
    }}

    img {{
      width: 100%;
      height: 100%;
      display: block;
      object-fit: cover;
    }}

    .info {{
      padding: 10px 11px 12px;
      display: grid;
      gap: 8px;
    }}

    .file {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 620;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .prompt {{
      min-width: 0;
      color: var(--ink);
      font-size: 14px;
      line-height: 1.35;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      cursor: default;
    }}

    .card-actions {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 8px;
      align-items: center;
    }}

    .card-actions button {{
      min-height: 34px;
      padding: 0 10px;
      font-size: 13px;
      font-weight: 720;
    }}

    .copy-button {{
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
      box-shadow: 0 8px 18px rgba(46, 111, 115, 0.22);
    }}

    .copy-button:hover:not(:disabled) {{
      background: var(--accent-dark);
      border-color: var(--accent-dark);
      color: #fff;
      transform: translateY(-1px);
    }}

    .preview-button {{
      background: var(--soft-panel);
      color: var(--ink);
    }}

    .card:hover,
    .card.hovered {{
      border-color: var(--accent);
      z-index: 5;
      box-shadow: var(--shadow);
      transform: translateY(-1px);
    }}

    .card:hover .hover-prompt,
    .card:focus-within .hover-prompt,
    .card.hovered .hover-prompt {{
      display: block;
    }}

    .hover-prompt {{
      display: none;
      position: absolute;
      left: 8px;
      right: 8px;
      top: calc(100% + 8px);
      z-index: 20;
      max-height: 260px;
      overflow: auto;
      padding: 12px;
      background: #171b1d;
      color: #fff;
      border-radius: 8px;
      box-shadow: 0 20px 56px rgba(0, 0, 0, 0.32);
      font-size: 13px;
      line-height: 1.45;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    .error {{
      color: var(--error);
      font-weight: 650;
    }}

    dialog {{
      width: min(1040px, calc(100vw - 32px));
      border: 0;
      border-radius: 8px;
      padding: 0;
      box-shadow: 0 28px 80px rgba(0, 0, 0, 0.34);
    }}

    dialog::backdrop {{
      background: rgba(16, 18, 18, 0.62);
    }}

    .modal {{
      display: grid;
      grid-template-columns: minmax(300px, 48%) minmax(0, 1fr);
      max-height: min(820px, calc(100vh - 48px));
      background: var(--panel);
      overflow: hidden;
    }}

    .modal-image {{
      width: 100%;
      height: 100%;
      min-height: 560px;
      object-fit: contain;
      background: #141718;
    }}

    .modal-body {{
      min-height: 0;
      display: grid;
      grid-template-rows: auto 1fr auto;
      gap: 12px;
      padding: 18px;
    }}

    .modal-body h2 {{
      margin: 0;
      font-size: 22px;
      letter-spacing: 0;
    }}

    .modal-prompt {{
      min-height: 0;
      overflow: auto;
      padding: 12px 0;
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      white-space: pre-wrap;
      font-size: 14px;
    }}

    .modal-actions {{
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 8px;
    }}

    .modal-actions .copy-button {{
      min-width: 126px;
    }}

    @media (max-width: 1100px) {{
      :root {{
        --cols: 4;
      }}
    }}

    @media (max-width: 820px) {{
      :root {{
        --cols: 3;
      }}

      .top {{
        align-items: start;
        flex-direction: column;
      }}
    }}

    @media (max-width: 580px) {{
      :root {{
        --cols: 2;
      }}

      main,
      .bar {{
        padding-left: 12px;
        padding-right: 12px;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="bar">
      <div class="top">
        <div>
          <h1>{escaped_title}</h1>
          <p class="summary"><span id="total"></span> images, {per_page} per page. Hover any card to read the full prompt.</p>
        </div>
        <div class="pager" aria-label="Pagination">
          <button id="prev" type="button">Prev</button>
          <div id="pageNumbers" class="pager"></div>
          <button id="next" type="button">Next</button>
          <span id="readout" class="readout"></span>
        </div>
      </div>
      <div class="controls" aria-label="Grid controls">
        <label class="control">Columns <input id="cols" type="range" min="2" max="8" value="5"><output id="colsOut">5</output></label>
        <label class="control">Image size <input id="thumb" type="range" min="120" max="520" step="10" value="360"><output id="thumbOut">360</output></label>
        <label class="control">Gap <input id="gap" type="range" min="6" max="28" value="14"><output id="gapOut">14</output></label>
      </div>
    </div>
  </header>

  <main>
    <section id="grid" class="grid"></section>
  </main>

  <dialog id="previewDialog">
    <div class="modal">
      <img id="modalImage" class="modal-image" alt="">
      <div class="modal-body">
        <div>
          <h2 id="modalTitle"></h2>
          <div id="modalFile" class="file"></div>
        </div>
        <div id="modalPrompt" class="modal-prompt"></div>
        <div class="modal-actions">
          <button id="modalCopy" class="copy-button" type="button">Copy prompt</button>
          <button id="modalClose" class="preview-button" type="button">Close</button>
        </div>
      </div>
    </div>
  </dialog>

  <script>
    const records = {data};
    const perPage = {per_page};
    let page = 1;

    const root = document.documentElement;
    const grid = document.getElementById("grid");
    const total = document.getElementById("total");
    const readout = document.getElementById("readout");
    const pageNumbers = document.getElementById("pageNumbers");
    const prev = document.getElementById("prev");
    const next = document.getElementById("next");
    const dialog = document.getElementById("previewDialog");
    const modalImage = document.getElementById("modalImage");
    const modalTitle = document.getElementById("modalTitle");
    const modalFile = document.getElementById("modalFile");
    const modalPrompt = document.getElementById("modalPrompt");
    const modalCopy = document.getElementById("modalCopy");
    const modalClose = document.getElementById("modalClose");
    const totalPages = Math.max(1, Math.ceil(records.length / perPage));
    total.textContent = records.length;

    function escapeHtml(value) {{
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({{
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      }}[char]));
    }}

    function getPrompt(record) {{
      return record.prompt || record.error || "No prompt available.";
    }}

    async function copyText(text, button) {{
      try {{
        if (navigator.clipboard) {{
          await navigator.clipboard.writeText(text);
        }} else {{
          throw new Error("Clipboard API unavailable");
        }}
      }} catch (error) {{
        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.style.position = "fixed";
        textarea.style.left = "-9999px";
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        document.execCommand("copy");
        textarea.remove();
      }}

      const original = button.textContent;
      button.textContent = "Copied";
      setTimeout(() => (button.textContent = original), 1100);
    }}

    function openPreview(index) {{
      const record = records[index];
      const prompt = getPrompt(record);
      modalImage.src = record.image;
      modalImage.alt = `Image ${{index + 1}}`;
      modalTitle.textContent = `Image ${{index + 1}}`;
      modalFile.textContent = record.image;
      modalPrompt.textContent = prompt;
      modalCopy.dataset.prompt = prompt;
      dialog.showModal();
    }}

    function renderPagination() {{
      pageNumbers.innerHTML = "";
      for (let index = 1; index <= totalPages; index += 1) {{
        const button = document.createElement("button");
        button.type = "button";
        button.className = index === page ? "page-number active" : "page-number";
        button.textContent = index;
        button.setAttribute("aria-label", `Page ${{index}}`);
        button.addEventListener("click", () => {{
          page = index;
          render();
          window.scrollTo({{ top: 0, behavior: "smooth" }});
        }});
        pageNumbers.appendChild(button);
      }}
    }}

    function render() {{
      const start = (page - 1) * perPage;
      const visible = records.slice(start, start + perPage);
      grid.innerHTML = visible.map((record, offset) => {{
        const index = start + offset + 1;
        const prompt = getPrompt(record);
        const errorClass = record.error ? " error" : "";
        return `<article class="card" tabindex="0">
          <div class="thumb" data-action="preview" data-index="${{start + offset}}"><img src="${{escapeHtml(record.image)}}" alt="Image ${{index}}" loading="lazy"></div>
          <div class="hover-prompt${{errorClass}}">${{escapeHtml(prompt)}}</div>
          <div class="info">
            <div class="file">${{index}} · ${{escapeHtml(record.image)}}</div>
            <div class="prompt${{errorClass}}">${{escapeHtml(prompt)}}</div>
            <div class="card-actions">
              <button class="copy-button" type="button" data-action="copy" data-index="${{start + offset}}" aria-label="Copy prompt for image ${{index}}">Copy</button>
              <button class="preview-button" type="button" data-action="preview" data-index="${{start + offset}}" aria-label="Preview image ${{index}}">Open</button>
            </div>
          </div>
        </article>`;
      }}).join("");

      prev.disabled = page === 1;
      next.disabled = page === totalPages;
      const end = Math.min(start + visible.length, records.length);
      readout.textContent = `${{start + 1}}-${{end}} of ${{records.length}}`;
      renderPagination();
    }}

    prev.addEventListener("click", () => {{
      if (page > 1) {{
        page -= 1;
        render();
        window.scrollTo({{ top: 0, behavior: "smooth" }});
      }}
    }});

    next.addEventListener("click", () => {{
      if (page < totalPages) {{
        page += 1;
        render();
        window.scrollTo({{ top: 0, behavior: "smooth" }});
      }}
    }});

    grid.addEventListener("mouseover", (event) => {{
      const card = event.target.closest(".card");
      if (card) card.classList.add("hovered");
    }});

    grid.addEventListener("mouseout", (event) => {{
      const card = event.target.closest(".card");
      if (card) card.classList.remove("hovered");
    }});

    grid.addEventListener("click", (event) => {{
      const target = event.target.closest("[data-action]");
      if (!target) return;
      const index = Number(target.dataset.index);
      const record = records[index];
      if (target.dataset.action === "copy") {{
        copyText(getPrompt(record), target);
      }}
      if (target.dataset.action === "preview") {{
        openPreview(index);
      }}
    }});

    grid.addEventListener("keydown", (event) => {{
      if (event.key !== "Enter" && event.key !== " ") return;
      if (event.target.closest("[data-action]")) return;
      const card = event.target.closest(".card");
      if (!card) return;
      const index = Array.from(grid.children).indexOf(card) + (page - 1) * perPage;
      event.preventDefault();
      openPreview(index);
    }});

    modalCopy.addEventListener("click", () => copyText(modalCopy.dataset.prompt || "", modalCopy));
    modalClose.addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", (event) => {{
      if (event.target === dialog) dialog.close();
    }});

    function bindRange(id, cssVar, suffix) {{
      const input = document.getElementById(id);
      const output = document.getElementById(`${{id}}Out`);
      function apply() {{
        output.textContent = input.value;
        root.style.setProperty(cssVar, `${{input.value}}${{suffix}}`);
      }}
      input.addEventListener("input", apply);
      apply();
    }}

    bindRange("cols", "--cols", "");
    bindRange("thumb", "--thumb", "px");
    bindRange("gap", "--gap", "px");
    render();
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a simple paginated grid preview from image prompt JSONL.")
    parser.add_argument("--input", default="image_prompts_final.jsonl")
    parser.add_argument("--output", default="prompt_preview_simple.html")
    parser.add_argument("--title", default="Image Prompt Grid")
    parser.add_argument("--per-page", type=int, default=100)
    args = parser.parse_args()

    records = load_records(Path(args.input))
    Path(args.output).write_text(build_html(records, args.title, args.per_page), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
