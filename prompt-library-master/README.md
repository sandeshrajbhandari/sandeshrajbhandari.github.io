# Prompt Library Master

Combined static prompt libraries for publishing on a personal GitHub site.

## Libraries

- [`ernie-prompts-awesome`](./ernie-prompts-awesome/) - ERNIE prompt image gallery
- [`z-image-turbo-prompts`](./z-image-turbo-prompts/) - Z-Image Turbo prompt gallery
- [`process.html`](./process.html) - short build notes for sources, prompt generation, and classification

Each folder is self-contained and can be copied into a static site. Open the
folder's `index.html` directly, or serve the repository with any static file
server.

## Notes

- Z-Image local WebP files are optional. The gallery falls back to the original
  hosted image URLs when `images/*.webp` files are not present.
- ERNIE images and prompts were scraped from `https://ernieimageprompt.com/`.
- Z-Image images came from `https://modelscope.cn/studios/Tongyi-MAI/Z-Image-Gallery`;
  prompts were generated locally with Qwen3.5 9B GGUF through llama.cpp.
- The old standalone repositories are archived; new updates live here.
