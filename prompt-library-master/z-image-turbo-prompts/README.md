# Z-Image Turbo Prompt Library

> **Archived:** This standalone prompt library is now maintained in the combined
> [prompt-library-master](https://github.com/sandeshrajbhandari/prompt-library-master)
> repository.

A static prompt browser for the Z-Image Turbo prompt set.

Open `index.html` directly or serve this folder with any static file server. The
preview uses local `images/*.webp` files when present and falls back to the
original hosted image URLs from `prompts.json`.

## Features

- Search, category filters, and tag filters
- Randomized grid order by default, with a static-order switch
- Prompt copy buttons on grid cards and in the detail modal
- Image detail modal with contained image preview and scrollable prompt text
- Modal prompt classification script in `classify_prompts_modal.py`
