"""Classify Z-Image prompts into categories and tags with Modal.

Run with:
    python3 -m modal run classify_prompts_modal.py --input-path prompts.json --output-path prompt_categories.js

This mirrors the Ernie prompt gallery classifier model and adds a multi-label
tag pass for the Z-Image filter UI.
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
CATEGORY_CANDIDATES = {
    "people portraits fashion beauty and character design": "Characters & Fashion",
    "rooms buildings landscapes architecture travel and environmental scenes": "Scenes & Architecture",
    "commercial products jewelry cosmetics packaging and retail objects": "Product & Commercial",
    "food drinks meals recipes restaurants desserts and ingredients": "Food & Lifestyle",
    "infographics maps diagrams posters typography readable text and layout design": "Infographics & Text",
    "photo manipulation editing compositing overlays object removal replacement and visual effects": "Photo Editing & Effects",
    "stylized illustration anime 3D render craft toys miniatures and handmade art": "Craft & 3D Styles",
}
TAG_LABELS = [
    "Portraits",
    "Fashion",
    "Beauty",
    "Jewelry",
    "Products",
    "Interiors",
    "Architecture",
    "Travel",
    "Food & Drink",
    "Nature",
    "Animals",
    "Vehicles",
    "Sports & Fitness",
    "Illustration",
    "3D Render",
    "Craft",
    "Text & Signs",
    "Maps & Diagrams",
    "Photo Effects",
    "Events",
]
CATEGORY_TEMPLATE = "This image generation prompt is best categorized as {}."
TAG_TEMPLATE = "This image generation prompt has the visual tag {}."
CHUNK_TOKEN_LIMIT = 820
TOKEN_BUCKETS = [
    ("short", 256),
    ("medium", 512),
    ("long", 820),
]
MIN_CATEGORY_CONFIDENCE = 0.24
CATEGORY_KEYWORDS = {
    "Characters & Fashion": [
        "person",
        "people",
        "portrait",
        "woman",
        "man",
        "girl",
        "boy",
        "child",
        "couple",
        "bride",
        "wedding",
        "model",
        "fashion",
        "dress",
        "outfit",
        "wearing",
        "clothing",
        "makeup",
        "hair",
        "selfie",
        "anime",
        "character",
        "elf",
        "doll",
        "cyclist",
    ],
    "Scenes & Architecture": [
        "interior",
        "room",
        "living room",
        "bedroom",
        "kitchen",
        "architecture",
        "building",
        "street",
        "city",
        "urban",
        "harbor",
        "canal",
        "bridge",
        "landscape",
        "mountain",
        "lake",
        "beach",
        "travel",
        "temple",
        "restaurant",
        "studio",
        "shop",
        "store",
        "office",
        "home",
        "park",
        "outdoor",
        "forest",
        "garden",
    ],
    "Product & Commercial": [
        "product",
        "jewelry",
        "necklace",
        "bracelet",
        "ring",
        "watch",
        "perfume",
        "cosmetic",
        "bottle",
        "packaging",
        "commercial",
        "advertising",
        "studio product",
        "flat-lay",
        "display",
        "bag",
        "shoes",
        "dress hanging",
        "label",
        "brand",
        "mockup",
        "box",
        "gift",
    ],
    "Food & Lifestyle": [
        "food",
        "restaurant",
        "dining",
        "meal",
        "salad",
        "sashimi",
        "sushi",
        "dessert",
        "cake",
        "coffee",
        "drink",
        "champagne",
        "breakfast",
        "pasta",
        "recipe",
        "ingredient",
        "kitchen",
        "table",
        "tea",
    ],
    "Infographics & Text": [
        "text",
        "typography",
        "poster",
        "infographic",
        "diagram",
        "map",
        "logo",
        "calligraphy",
        "chart",
        "layout",
        "book",
        "menu",
        "handwritten",
        "title",
        "lettering",
        "sign reads",
    ],
    "Photo Editing & Effects": [
        "effect",
        "overlay",
        "glass effect",
        "raindrop",
        "rain",
        "reflection effect",
        "bokeh effect",
        "blur effect",
        "composited",
        "refraction",
        "double exposure",
        "remove",
        "replace",
        "retouch",
        "transparent glass",
    ],
    "Craft & 3D Styles": [
        "3d",
        "render",
        "c4d",
        "illustration",
        "watercolor",
        "cartoon",
        "felt",
        "wool",
        "clay",
        "miniature",
        "handcrafted",
        "toy",
        "paper",
        "origami",
        "sketch",
        "line-art",
        "diorama",
        "stop-motion",
        "bjd",
    ],
}


app = modal.App("z-image-prompt-gallery-classifier")
image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "accelerate",
    "sentencepiece",
    "torch",
    "transformers",
)


@app.cls(image=image, cpu=4.0, memory=8192, gpu="T4", timeout=1200, scaledown_window=120)
class PromptClassifier:
    @modal.enter()
    def load_model(self) -> None:
        import torch
        from transformers import AutoTokenizer, pipeline

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.classifier = pipeline(
            "zero-shot-classification",
            model=MODEL_ID,
            device=0 if torch.cuda.is_available() else -1,
        )

    @modal.method()
    def classify_batch(self, prompts: list[dict[str, str]], top_tags: int) -> list[dict[str, Any]]:
        prompt_chunks: list[dict[str, Any]] = []
        sequences: list[str] = []

        for prompt in prompts:
            chunks, token_count, token_bucket = self.prompt_chunks(prompt["text"])
            prompt_chunks.append(
                {
                    "prompt": prompt,
                    "token_count": token_count,
                    "token_bucket": token_bucket,
                    "chunk_count": len(chunks),
                    "chunk_indexes": list(range(len(sequences), len(sequences) + len(chunks))),
                }
            )
            sequences.extend(chunks)

        category_results = self.classifier(
            sequences,
            candidate_labels=list(CATEGORY_CANDIDATES.keys()),
            hypothesis_template=CATEGORY_TEMPLATE,
            multi_label=False,
            truncation=False,
            batch_size=8,
        )
        tag_results = self.classifier(
            sequences,
            candidate_labels=TAG_LABELS,
            hypothesis_template=TAG_TEMPLATE,
            multi_label=True,
            truncation=False,
            batch_size=8,
        )
        if isinstance(category_results, dict):
            category_results = [category_results]
        if isinstance(tag_results, dict):
            tag_results = [tag_results]

        classifications: list[dict[str, Any]] = []
        for prompt_info in prompt_chunks:
            prompt = prompt_info["prompt"]
            chunk_indexes = prompt_info["chunk_indexes"]
            category = self.aggregate_results(
                [category_results[index] for index in chunk_indexes],
                list(CATEGORY_CANDIDATES.keys()),
            )
            classifier_category = CATEGORY_CANDIDATES[category["labels"][0]]
            classifier_confidence = float(category["scores"][0])
            category_label, category_source = resolve_category(
                prompt["text"], classifier_category, classifier_confidence
            )
            tags = self.aggregate_results(
                [tag_results[index] for index in chunk_indexes],
                TAG_LABELS,
            )
            tag_items = [
                {"tag": label, "confidence": round(float(score), 4)}
                for label, score in zip(tags["labels"], tags["scores"], strict=True)
            ][:top_tags]
            classifications.append(
                {
                    "id": prompt["id"],
                    "image": prompt["image"],
                    "category": category_label,
                    "classifier_label": category["labels"][0],
                    "confidence": round(classifier_confidence, 4),
                    "category_source": category_source,
                    "tags": [item["tag"] for item in tag_items],
                    "tag_scores": tag_items,
                    "token_count": prompt_info["token_count"],
                    "token_bucket": prompt_info["token_bucket"],
                    "chunk_count": prompt_info["chunk_count"],
                }
            )

        return classifications

    def prompt_chunks(self, text: str) -> tuple[list[str], int, str]:
        token_ids = self.tokenizer(text, add_special_tokens=False)["input_ids"]
        token_count = len(token_ids)
        token_bucket = self.token_bucket(token_count)

        if token_count <= CHUNK_TOKEN_LIMIT:
            return [text], token_count, token_bucket

        chunks: list[str] = []
        for start in range(0, token_count, CHUNK_TOKEN_LIMIT):
            chunk_ids = token_ids[start : start + CHUNK_TOKEN_LIMIT]
            chunks.append(self.tokenizer.decode(chunk_ids, skip_special_tokens=True))

        return chunks, token_count, token_bucket

    def token_bucket(self, token_count: int) -> str:
        for name, ceiling in TOKEN_BUCKETS:
            if token_count <= ceiling:
                return name

        return "chunked"

    def aggregate_results(
        self, results: list[dict[str, Any]], candidate_labels: list[str]
    ) -> dict[str, list[Any]]:
        if len(results) == 1:
            return results[0]

        score_totals = {label: 0.0 for label in candidate_labels}
        for result in results:
            for label, score in zip(result["labels"], result["scores"], strict=True):
                score_totals[label] += float(score)

        averaged_scores = [
            (label, score_totals[label] / len(results)) for label in candidate_labels
        ]
        averaged_scores.sort(key=lambda item: item[1], reverse=True)

        return {
            "labels": [label for label, _score in averaged_scores],
            "scores": [score for _label, score in averaged_scores],
        }


@app.local_entrypoint()
def main(
    input_path: str = "prompts.json",
    output_path: str = "prompt_categories.js",
    batch_size: int = 24,
    top_tags: int = 5,
) -> None:
    records = load_gallery(Path(input_path))
    prompts = [to_prompt_payload(record, offset) for offset, record in enumerate(records)]
    classifier = PromptClassifier()
    classifications: list[dict[str, Any]] = []
    batches = bucketed_batches(prompts, batch_size)

    for batch_number, batch in enumerate(batches, start=1):
        classifications.extend(classifier.classify_batch.remote(batch, top_tags))
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
    image = str(record.get("image") or "")
    prompt_parts = [
        str(record.get("title") or ""),
        str(record.get("prompt") or ""),
    ]
    text = "\n".join(part for part in prompt_parts if part)

    return {
        "id": image_index(image) or str(offset),
        "image": image,
        "text": text,
        "estimated_token_bucket": estimated_token_bucket(text),
    }


def image_index(image: str) -> str:
    match = re.search(r"(\d+)(?=\.[a-z0-9]+$)", image, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def write_classifications(path: Path, classifications: list[dict[str, Any]]) -> None:
    items: dict[str, dict[str, Any]] = {}
    for item in classifications:
        record = {
            "category": item["category"],
            "classifier_label": item["classifier_label"],
            "confidence": item["confidence"],
            "category_source": item["category_source"],
            "tags": item["tags"],
            "tag_scores": item["tag_scores"],
            "token_count": item["token_count"],
            "token_bucket": item["token_bucket"],
            "chunk_count": item["chunk_count"],
        }
        items[item["id"]] = record
        if item["image"]:
            items[item["image"]] = record

    payload = {
        "model": MODEL_ID,
        "labels": CATEGORY_LABELS,
        "tagLabels": TAG_LABELS,
        "chunkTokenLimit": CHUNK_TOKEN_LIMIT,
        "minCategoryConfidence": MIN_CATEGORY_CONFIDENCE,
        "items": items,
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


def bucketed_batches(items: list[dict[str, str]], size: int) -> list[list[dict[str, str]]]:
    buckets: dict[str, list[dict[str, str]]] = {
        "short": [],
        "medium": [],
        "long": [],
        "chunked": [],
    }

    for item in items:
        buckets[item["estimated_token_bucket"]].append(item)

    batches: list[list[dict[str, str]]] = []
    for bucket_name in ("short", "medium", "long", "chunked"):
        batches.extend(chunked(buckets[bucket_name], size))

    print(
        "Token bucket estimates: "
        + ", ".join(f"{name}={len(values)}" for name, values in buckets.items()),
        flush=True,
    )
    return batches


def estimated_token_bucket(text: str) -> str:
    tokenish_count = len(re.findall(r"\w+|[^\s\w]", text))
    for name, ceiling in TOKEN_BUCKETS:
        if tokenish_count <= ceiling:
            return name

    return "chunked"


def resolve_category(
    text: str, classifier_category: str, classifier_confidence: float
) -> tuple[str, str]:
    keyword_category, keyword_score = keyword_category_score(text)
    if classifier_confidence >= MIN_CATEGORY_CONFIDENCE:
        return classifier_category, "classifier"
    if keyword_score > 0:
        return keyword_category, "keyword_fallback"
    return classifier_category, "classifier_low_confidence"


def keyword_category_score(text: str) -> tuple[str, int]:
    normalized_text = " " + text.lower() + " "
    best_category = "Other Concepts"
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(
            keyword_weight(keyword)
            for keyword in keywords
            if keyword.lower() in normalized_text
        )
        if score > best_score:
            best_category = category
            best_score = score

    return best_category, best_score


def keyword_weight(keyword: str) -> int:
    return 3 if len(keyword) > 8 else 2
