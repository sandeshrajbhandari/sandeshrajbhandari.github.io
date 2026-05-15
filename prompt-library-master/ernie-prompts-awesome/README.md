# Prompt Image Gallery

> **Archived:** This standalone prompt library is now maintained in the combined
> [prompt-library-master](https://github.com/sandeshrajbhandari/prompt-library-master)
> repository.

A lightweight static frontend for browsing the image prompt data in `prompts.json`.

## Run locally

Serve the repository root with any static file server:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Features

- Responsive image grid backed by `window.__GALLERY_DATA__` from `prompts.json`
- Prompt preview overlay on image hover/focus
- Clickable detail modal with the full image, prompt, revised prompt, author, and source
- Pagination capped at 60 images per page
- Prompt categories derived from English prompt text, with category and search filters

## Modal prompt classification

The frontend includes a deterministic keyword fallback so it works offline immediately. To generate
model-based categories, install and authenticate the Modal CLI, then run:

```bash
modal run scripts/classify_prompts_modal.py --input-path prompts.json --output-path prompt_categories.js
```

The Modal job uses `valhalla/distilbart-mnli-12-3`, a compact MNLI zero-shot classifier that is
well suited to fast broad-category text classification without training custom labels. The generated
`prompt_categories.js` file is loaded by the frontend and overrides the local fallback categories.
