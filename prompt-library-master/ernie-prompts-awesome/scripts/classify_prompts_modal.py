"""Classify gallery prompts into broad UI categories with Modal.

Run with:
    modal run scripts/classify_prompts_modal.py --input-path prompts.json --output-path prompt_categories.js

The script uses a compact MNLI zero-shot model so new prompts can be categorized
without maintaining a large hand-labeled training set.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import modal


MODEL_ID = "valhalla/distilbart-mnli-12-3"
CATEGORY_LABELS = [
    "Characters & Fashion",
    "Scenes & Architecture",
    "Product & Commercial",
    "Food & Lifestyle",
    "Infographics & Text",
    "Photo Editing & Effects",
    "Craft & 3D Styles",
    "Other Concepts",
]
HYPOTHESIS_TEMPLATE = "This image generation prompt belongs to the {} category."


app = modal.App("prompt-gallery-classifier")
image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "accelerate",
    "sentencepiece",
    "torch",
    "transformers",
)


@app.cls(image=image, cpu=4.0, memory=8192, gpu="T4", timeout=900, scaledown_window=120)
class PromptClassifier:
    @modal.enter()
    def load_model(self) -> None:
        import torch
        from transformers import pipeline

        self.classifier = pipeline(
            "zero-shot-classification",
            model=MODEL_ID,
            device=0 if torch.cuda.is_available() else -1,
        )

    @modal.method()
    def classify_batch(self, prompts: list[dict[str, str]]) -> list[dict[str, Any]]:
        classifications: list[dict[str, Any]] = []

        for prompt in prompts:
            result = self.classifier(
                prompt["text"],
                candidate_labels=CATEGORY_LABELS,
                hypothesis_template=HYPOTHESIS_TEMPLATE,
                multi_label=False,
                truncation=True,
                max_length=384,
            )
            classifications.append(
                {
                    "id": prompt["id"],
                    "category": result["labels"][0],
                    "confidence": round(float(result["scores"][0]), 4),
                }
            )

        return classifications


@app.local_entrypoint()
def main(
    input_path: str = "prompts.json",
    output_path: str = "prompt_categories.js",
    batch_size: int = 32,
) -> None:
    records = load_gallery(Path(input_path))
    prompts = [to_prompt_payload(record, offset) for offset, record in enumerate(records)]
    classifier = PromptClassifier()
    classifications: list[dict[str, Any]] = []

    batches = chunked(prompts, batch_size)

    for batch_number, batch in enumerate(batches, start=1):
        classifications.extend(classifier.classify_batch.remote(batch))
        print(f"Classified batch {batch_number}/{len(batches)}", flush=True)

    write_classifications(Path(output_path), classifications)
    print(f"Wrote {len(classifications)} classifications to {output_path}")


def load_gallery(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    text = re.sub(r"^window\.__GALLERY_DATA__\s*=\s*", "", text).rstrip(";")
    data = json.loads(text)

    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a gallery array")

    return data


def to_prompt_payload(record: dict[str, Any], offset: int) -> dict[str, str]:
    prompt_parts = [
        record.get("title_en") or record.get("title") or "",
        record.get("prompt_en") or record.get("prompt") or "",
    ]
    text = "\n".join(part for part in prompt_parts if part)

    return {
        "id": record.get("filename") or str(record.get("index") or offset),
        "text": text[:1200],
    }


def write_classifications(path: Path, classifications: list[dict[str, Any]]) -> None:
    payload = {
        "model": MODEL_ID,
        "labels": CATEGORY_LABELS,
        "items": {
            item["id"]: {
                "category": item["category"],
                "confidence": item["confidence"],
            }
            for item in classifications
        },
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)

    if path.suffix == ".js":
        path.write_text(f"window.__PROMPT_CLASSIFICATION__ = {serialized};\n", encoding="utf-8")
    else:
        path.write_text(serialized + "\n", encoding="utf-8")


def chunked(items: list[dict[str, str]], size: int) -> list[list[dict[str, str]]]:
    if size <= 0:
        raise ValueError("batch_size must be positive")

    return [items[index : index + size] for index in range(0, len(items), size)]
