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


def build_html(records: list[dict], title: str) -> str:
    data = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")
    escaped_title = html.escape(title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f1eb;
      --ink: #1f2326;
      --muted: #66706e;
      --panel: #ffffff;
      --line: #d9d4ca;
      --accent: #236c6f;
      --accent-2: #a44b37;
      --shadow: 0 18px 44px rgba(35, 42, 40, 0.11);
      --columns: 4;
      --image-size: 260px;
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

    button,
    input {{
      font: inherit;
    }}

    header {{
      position: sticky;
      top: 0;
      z-index: 20;
      background: rgba(244, 241, 235, 0.94);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--line);
    }}

    .bar {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 18px 22px;
      display: grid;
      gap: 14px;
    }}

    .topline {{
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 18px;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(25px, 3vw, 38px);
      line-height: 1;
      letter-spacing: 0;
    }}

    .meta {{
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 14px;
    }}

    .tabs,
    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}

    .tab {{
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      min-height: 36px;
      padding: 0 12px;
      border-radius: 8px;
      cursor: pointer;
    }}

    .tab.active {{
      background: var(--ink);
      color: #fff;
      border-color: var(--ink);
    }}

    .control {{
      min-height: 38px;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0 10px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--muted);
      font-size: 13px;
    }}

    .control output {{
      color: var(--ink);
      font-weight: 720;
      min-width: 32px;
      text-align: right;
    }}

    input[type="range"] {{
      accent-color: var(--accent);
      width: 120px;
    }}

    main {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 22px;
    }}

    .variation-note {{
      margin: 0 0 14px;
      color: var(--muted);
      font-size: 14px;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(var(--columns), minmax(0, 1fr));
      gap: var(--gap);
    }}

    .tile {{
      min-width: 0;
      position: relative;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 8px;
      overflow: visible;
      box-shadow: var(--shadow);
    }}

    .image-wrap {{
      position: relative;
      overflow: hidden;
      background: #e7e1d6;
    }}

    .tile img {{
      width: 100%;
      height: 100%;
      display: block;
      object-fit: cover;
    }}

    .prompt-line {{
      position: relative;
      min-width: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      color: var(--ink);
      cursor: pointer;
    }}

    .prompt-line:focus {{
      outline: 2px solid var(--accent);
      outline-offset: 3px;
    }}

    .hover-preview {{
      display: none;
      position: absolute;
      left: 0;
      right: 0;
      bottom: calc(100% + 8px);
      z-index: 30;
      padding: 12px;
      background: #15191a;
      color: #fff;
      border-radius: 8px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
      white-space: normal;
      font-size: 13px;
      line-height: 1.45;
      max-height: 230px;
      overflow: auto;
    }}

    .prompt-line:hover .hover-preview,
    .prompt-line:focus .hover-preview {{
      display: block;
    }}

    .file {{
      font-size: 12px;
      color: var(--muted);
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }}

    .open-btn {{
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      border-radius: 8px;
      min-height: 32px;
      padding: 0 10px;
      cursor: pointer;
    }}

    .open-btn:hover {{
      border-color: var(--accent);
      color: var(--accent);
    }}

    .v-contact .tile {{
      box-shadow: none;
    }}

    .v-contact .image-wrap {{
      height: var(--image-size);
      border-radius: 7px 7px 0 0;
    }}

    .v-contact .body {{
      padding: 10px;
      display: grid;
      gap: 8px;
    }}

    .v-contact .number {{
      position: absolute;
      top: 8px;
      left: 8px;
      min-width: 28px;
      height: 28px;
      display: grid;
      place-items: center;
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid rgba(0, 0, 0, 0.08);
      border-radius: 999px;
      font-size: 12px;
      font-weight: 800;
    }}

    .v-editorial .grid {{
      align-items: stretch;
    }}

    .v-editorial .tile {{
      min-height: calc(var(--image-size) + 72px);
      background: #121516;
      color: #fff;
      border-color: #24292a;
    }}

    .v-editorial .image-wrap {{
      height: calc(var(--image-size) + 70px);
      border-radius: 7px;
    }}

    .v-editorial .image-wrap::after {{
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(to top, rgba(0, 0, 0, 0.72), rgba(0, 0, 0, 0.08) 62%, rgba(0, 0, 0, 0));
    }}

    .v-editorial .body {{
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 2;
      padding: 14px;
      display: grid;
      gap: 7px;
    }}

    .v-editorial .file,
    .v-editorial .prompt-line {{
      color: #fff;
    }}

    .v-editorial .open-btn {{
      justify-self: start;
      color: #fff;
      background: rgba(255, 255, 255, 0.12);
      border-color: rgba(255, 255, 255, 0.34);
    }}

    .v-inspector {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(280px, 390px);
      gap: 18px;
      align-items: start;
    }}

    .v-inspector .grid {{
      grid-template-columns: repeat(var(--columns), minmax(110px, 1fr));
    }}

    .v-inspector .tile {{
      box-shadow: none;
      cursor: pointer;
    }}

    .v-inspector .tile.selected {{
      outline: 3px solid var(--accent);
      outline-offset: 2px;
    }}

    .v-inspector .image-wrap {{
      height: var(--image-size);
      border-radius: 7px 7px 0 0;
    }}

    .v-inspector .body {{
      padding: 9px;
      display: grid;
      gap: 6px;
    }}

    .inspector-panel {{
      position: sticky;
      top: 150px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      box-shadow: var(--shadow);
    }}

    .inspector-panel img {{
      width: 100%;
      height: min(46vh, 480px);
      object-fit: cover;
      display: block;
      background: #e7e1d6;
    }}

    .inspector-copy {{
      padding: 14px;
      display: grid;
      gap: 10px;
    }}

    .inspector-copy p {{
      margin: 0;
      color: var(--ink);
      font-size: 14px;
      max-height: 230px;
      overflow: auto;
    }}

    .v-board .grid {{
      grid-template-columns: repeat(var(--columns), minmax(260px, 1fr));
    }}

    .v-board .tile {{
      display: grid;
      grid-template-columns: minmax(92px, calc(var(--image-size) * 0.55)) minmax(0, 1fr);
      min-height: 128px;
      box-shadow: none;
    }}

    .v-board .image-wrap {{
      height: 100%;
      min-height: 128px;
      border-radius: 7px 0 0 7px;
    }}

    .v-board .body {{
      padding: 11px;
      display: grid;
      gap: 8px;
      align-content: center;
    }}

    .v-board .stats {{
      color: var(--accent-2);
      font-size: 12px;
      font-weight: 760;
    }}

    dialog {{
      width: min(980px, calc(100vw - 34px));
      border: 0;
      border-radius: 8px;
      padding: 0;
      box-shadow: 0 28px 80px rgba(0, 0, 0, 0.34);
    }}

    dialog::backdrop {{
      background: rgba(11, 14, 15, 0.58);
    }}

    .modal {{
      display: grid;
      grid-template-columns: minmax(240px, 43%) minmax(0, 1fr);
      max-height: min(780px, calc(100vh - 48px));
      overflow: hidden;
      background: #fff;
    }}

    .modal img {{
      width: 100%;
      height: 100%;
      min-height: 460px;
      object-fit: cover;
      background: #e7e1d6;
    }}

    .modal-body {{
      padding: 18px;
      display: grid;
      grid-template-rows: auto 1fr auto;
      gap: 12px;
      min-height: 0;
    }}

    .modal-body h2 {{
      margin: 0;
      font-size: 20px;
      letter-spacing: 0;
    }}

    .modal-prompt {{
      overflow: auto;
      white-space: pre-wrap;
      font-size: 14px;
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      padding: 12px 0;
    }}

    .modal-actions {{
      display: flex;
      justify-content: end;
      gap: 8px;
    }}

    @media (max-width: 900px) {{
      .topline {{
        align-items: start;
        flex-direction: column;
      }}

      .v-inspector {{
        grid-template-columns: 1fr;
      }}

      .inspector-panel {{
        position: static;
      }}

      .modal {{
        grid-template-columns: 1fr;
      }}

      .modal img {{
        min-height: 260px;
        max-height: 48vh;
      }}
    }}

    @media (max-width: 680px) {{
      :root {{
        --columns: 2;
      }}

      main,
      .bar {{
        padding-left: 14px;
        padding-right: 14px;
      }}

      .v-board .grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="bar">
      <div class="topline">
        <div>
          <h1>{escaped_title}</h1>
          <p class="meta"><span id="count"></span> sample prompts. Hover a prompt for a quick read, click any prompt or preview button for the full prompt.</p>
        </div>
        <div class="tabs" role="tablist" aria-label="Preview variations">
          <button class="tab active" type="button" data-variant="contact">Contact Sheet</button>
          <button class="tab" type="button" data-variant="editorial">Editorial Tiles</button>
          <button class="tab" type="button" data-variant="inspector">Inspector Grid</button>
          <button class="tab" type="button" data-variant="board">Prompt Board</button>
        </div>
      </div>
      <div class="controls" aria-label="Grid controls">
        <label class="control">Columns <input id="columns" type="range" min="2" max="8" value="4"><output id="columnsOut">4</output></label>
        <label class="control">Image height <input id="imageSize" type="range" min="120" max="440" step="10" value="260"><output id="imageSizeOut">260</output></label>
        <label class="control">Spacing <input id="gap" type="range" min="6" max="30" value="14"><output id="gapOut">14</output></label>
      </div>
    </div>
  </header>

  <main>
    <p class="variation-note" id="variationNote"></p>
    <section id="app" aria-live="polite"></section>
  </main>

  <dialog id="promptDialog">
    <div class="modal">
      <img id="modalImage" alt="">
      <div class="modal-body">
        <div>
          <h2 id="modalTitle"></h2>
          <div class="file" id="modalFile"></div>
        </div>
        <div class="modal-prompt" id="modalPrompt"></div>
        <div class="modal-actions">
          <button class="open-btn" id="copyPrompt" type="button">Copy prompt</button>
          <button class="open-btn" id="closeDialog" type="button">Close</button>
        </div>
      </div>
    </div>
  </dialog>

  <script>
    const records = {data};
    const state = {{ variant: "contact", selected: 0 }};
    const notes = {{
      contact: "Variation 1: a compact contact sheet for scanning many images quickly.",
      editorial: "Variation 2: larger visual tiles with prompt text over the image for a more visual review pass.",
      inspector: "Variation 3: a working grid with a sticky inspector panel for focused prompt editing or comparison.",
      board: "Variation 4: a denser prompt board with horizontal tiles for prompt-heavy review."
    }};

    const app = document.getElementById("app");
    const note = document.getElementById("variationNote");
    const root = document.documentElement;
    const dialog = document.getElementById("promptDialog");
    const modalImage = document.getElementById("modalImage");
    const modalTitle = document.getElementById("modalTitle");
    const modalFile = document.getElementById("modalFile");
    const modalPrompt = document.getElementById("modalPrompt");
    const copyPrompt = document.getElementById("copyPrompt");

    document.getElementById("count").textContent = records.length;

    function escapeHtml(value) {{
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({{
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      }}[char]));
    }}

    function wordCount(prompt) {{
      return String(prompt || "").trim().split(/\\s+/).filter(Boolean).length;
    }}

    function promptLine(record, index) {{
      const prompt = escapeHtml(record.prompt || record.error || "No prompt available.");
      return `<div class="prompt-line" tabindex="0" role="button" data-index="${{index}}" title="Open full prompt">${{prompt}}<span class="hover-preview">${{prompt}}</span></div>`;
    }}

    function openDialog(index) {{
      const record = records[index];
      modalImage.src = record.image;
      modalImage.alt = `Source image ${{index + 1}}`;
      modalTitle.textContent = `Image ${{index + 1}}`;
      modalFile.textContent = record.image;
      modalPrompt.textContent = record.prompt || record.error || "No prompt available.";
      copyPrompt.dataset.prompt = modalPrompt.textContent;
      dialog.showModal();
    }}

    function contactTile(record, index) {{
      return `<article class="tile">
        <div class="image-wrap"><img src="${{escapeHtml(record.image)}}" alt="Image ${{index + 1}}" loading="lazy"><div class="number">${{index + 1}}</div></div>
        <div class="body">
          <div class="file">${{escapeHtml(record.image)}}</div>
          ${{promptLine(record, index)}}
          <button class="open-btn" type="button" data-index="${{index}}">Preview</button>
        </div>
      </article>`;
    }}

    function editorialTile(record, index) {{
      return `<article class="tile">
        <div class="image-wrap"><img src="${{escapeHtml(record.image)}}" alt="Image ${{index + 1}}" loading="lazy"></div>
        <div class="body">
          <div class="file">Image ${{index + 1}} / ${{escapeHtml(record.image)}}</div>
          ${{promptLine(record, index)}}
          <button class="open-btn" type="button" data-index="${{index}}">Open prompt</button>
        </div>
      </article>`;
    }}

    function inspectorTile(record, index) {{
      const selected = index === state.selected ? " selected" : "";
      return `<article class="tile${{selected}}" data-select="${{index}}" tabindex="0">
        <div class="image-wrap"><img src="${{escapeHtml(record.image)}}" alt="Image ${{index + 1}}" loading="lazy"></div>
        <div class="body">
          <div class="file">Image ${{index + 1}}</div>
          ${{promptLine(record, index)}}
        </div>
      </article>`;
    }}

    function boardTile(record, index) {{
      return `<article class="tile">
        <div class="image-wrap"><img src="${{escapeHtml(record.image)}}" alt="Image ${{index + 1}}" loading="lazy"></div>
        <div class="body">
          <div class="file">${{escapeHtml(record.image)}}</div>
          <div class="stats">${{wordCount(record.prompt)}} words</div>
          ${{promptLine(record, index)}}
          <button class="open-btn" type="button" data-index="${{index}}">Read full</button>
        </div>
      </article>`;
    }}

    function renderInspectorPanel() {{
      const record = records[state.selected] || records[0];
      return `<aside class="inspector-panel">
        <img src="${{escapeHtml(record.image)}}" alt="Selected image">
        <div class="inspector-copy">
          <div>
            <div class="file">Selected: ${{escapeHtml(record.image)}}</div>
            <strong>Image ${{state.selected + 1}}</strong>
          </div>
          <p>${{escapeHtml(record.prompt || record.error || "No prompt available.")}}</p>
          <button class="open-btn" type="button" data-index="${{state.selected}}">Open modal preview</button>
        </div>
      </aside>`;
    }}

    function render() {{
      note.textContent = notes[state.variant];
      document.querySelectorAll(".tab").forEach((button) => {{
        button.classList.toggle("active", button.dataset.variant === state.variant);
      }});

      if (state.variant === "contact") {{
        app.className = "v-contact";
        app.innerHTML = `<div class="grid">${{records.map(contactTile).join("")}}</div>`;
      }}
      if (state.variant === "editorial") {{
        app.className = "v-editorial";
        app.innerHTML = `<div class="grid">${{records.map(editorialTile).join("")}}</div>`;
      }}
      if (state.variant === "inspector") {{
        app.className = "v-inspector";
        app.innerHTML = `<div class="grid">${{records.map(inspectorTile).join("")}}</div>${{renderInspectorPanel()}}`;
      }}
      if (state.variant === "board") {{
        app.className = "v-board";
        app.innerHTML = `<div class="grid">${{records.map(boardTile).join("")}}</div>`;
      }}
    }}

    document.querySelectorAll(".tab").forEach((button) => {{
      button.addEventListener("click", () => {{
        state.variant = button.dataset.variant;
        render();
      }});
    }});

    function bindRange(id, cssVar, suffix) {{
      const input = document.getElementById(id);
      const out = document.getElementById(`${{id}}Out`);
      function apply() {{
        out.textContent = input.value;
        root.style.setProperty(cssVar, `${{input.value}}${{suffix}}`);
      }}
      input.addEventListener("input", apply);
      apply();
    }}

    bindRange("columns", "--columns", "");
    bindRange("imageSize", "--image-size", "px");
    bindRange("gap", "--gap", "px");

    app.addEventListener("click", (event) => {{
      const selectTile = event.target.closest("[data-select]");
      if (selectTile) {{
        state.selected = Number(selectTile.dataset.select);
        render();
        return;
      }}

      const openTarget = event.target.closest("[data-index]");
      if (openTarget) {{
        openDialog(Number(openTarget.dataset.index));
      }}
    }});

    app.addEventListener("keydown", (event) => {{
      if (event.key !== "Enter" && event.key !== " ") return;
      const target = event.target.closest("[data-index], [data-select]");
      if (!target) return;
      event.preventDefault();
      if (target.dataset.select) {{
        state.selected = Number(target.dataset.select);
        render();
      }} else {{
        openDialog(Number(target.dataset.index));
      }}
    }});

    document.getElementById("closeDialog").addEventListener("click", () => dialog.close());
    copyPrompt.addEventListener("click", async () => {{
      await navigator.clipboard.writeText(copyPrompt.dataset.prompt || "");
      copyPrompt.textContent = "Copied";
      setTimeout(() => (copyPrompt.textContent = "Copy prompt"), 1200);
    }});

    render();
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an interactive four-variation grid preview from prompt JSONL.")
    parser.add_argument("--input", default="image_prompts_10_fewshot.jsonl")
    parser.add_argument("--output", default="prompt_preview_variations_sample.html")
    parser.add_argument("--title", default="Prompt Preview Grid Variations")
    args = parser.parse_args()

    records = load_records(Path(args.input))
    Path(args.output).write_text(build_html(records, args.title), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
