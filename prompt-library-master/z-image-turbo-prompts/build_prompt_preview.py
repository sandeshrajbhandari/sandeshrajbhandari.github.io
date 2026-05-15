#!/usr/bin/env python3
import argparse
import html
import json
from pathlib import Path


def load_records(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            records.append(json.loads(line))
    return records


def render_record(record: dict, index: int) -> str:
    image = html.escape(record.get("image", ""))
    prompt = record.get("prompt")
    error = record.get("error")
    elapsed = record.get("elapsed_seconds")
    meta = f"{image}"
    if elapsed is not None:
        meta += f" · {elapsed}s"

    body = (
        f'<p class="prompt">{html.escape(prompt)}</p>'
        if prompt
        else f'<p class="error">{html.escape(error or "No prompt generated.")}</p>'
    )

    return f"""
      <article class="card">
        <figure>
          <img src="{image}" alt="Source image {index}" loading="lazy">
        </figure>
        <section>
          <div class="kicker">Image {index}</div>
          <h2>{html.escape(meta)}</h2>
          {body}
        </section>
      </article>"""


def build_html(records: list[dict], title: str) -> str:
    cards = "\n".join(render_record(record, index) for index, record in enumerate(records, start=1))
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
      --bg: #f6f3ee;
      --ink: #202020;
      --muted: #68635c;
      --panel: #ffffff;
      --line: #ded8cf;
      --accent: #2f6f73;
      --error: #9d2f2f;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}

    header {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px 18px;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(28px, 4vw, 44px);
      line-height: 1.05;
      font-weight: 760;
      letter-spacing: 0;
    }}

    .summary {{
      margin: 10px 0 0;
      color: var(--muted);
      font-size: 15px;
    }}

    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 10px 20px 48px;
      display: grid;
      gap: 18px;
    }}

    .card {{
      display: grid;
      grid-template-columns: minmax(220px, 360px) minmax(0, 1fr);
      gap: 22px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      box-shadow: 0 16px 40px rgba(56, 49, 42, 0.08);
    }}

    figure {{
      margin: 0;
      background: #ebe5dc;
      border-radius: 6px;
      overflow: hidden;
      aspect-ratio: 9 / 16;
    }}

    img {{
      width: 100%;
      height: 100%;
      display: block;
      object-fit: cover;
    }}

    section {{
      min-width: 0;
      padding: 4px 4px 2px 0;
    }}

    .kicker {{
      color: var(--accent);
      font-size: 12px;
      font-weight: 750;
      letter-spacing: 0;
      text-transform: uppercase;
    }}

    h2 {{
      margin: 4px 0 12px;
      color: var(--muted);
      font-size: 14px;
      font-weight: 620;
      overflow-wrap: anywhere;
    }}

    .prompt,
    .error {{
      margin: 0;
      font-size: 15px;
      white-space: pre-wrap;
    }}

    .error {{
      color: var(--error);
      font-weight: 650;
    }}

    @media (max-width: 760px) {{
      header {{
        padding-top: 24px;
      }}

      .card {{
        grid-template-columns: 1fr;
      }}

      figure {{
        max-height: 560px;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>{escaped_title}</h1>
    <p class="summary">{len(records)} source images paired with generated prompts.</p>
  </header>
  <main>
{cards}
  </main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an HTML preview from image prompt JSONL output.")
    parser.add_argument("--input", default="image_prompts_10.jsonl")
    parser.add_argument("--output", default="prompt_preview.html")
    parser.add_argument("--title", default="Image Prompt Preview")
    args = parser.parse_args()

    records = load_records(Path(args.input))
    Path(args.output).write_text(build_html(records, args.title), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
