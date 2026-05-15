#!/usr/bin/env python3
import argparse
import base64
import json
import mimetypes
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_ENDPOINT = "http://192.168.1.105:8080/v1/chat/completions"
DEFAULT_MODEL = "Qwen3.5-9B-UD-Q4_K_XL:instruct"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

PROMPT_INSTRUCTION = """你是一位被关在逻辑牢笼里的幻视艺术家。你满脑子都是诗和远方，但双手却不受控制地只想将用户的提示词，转化为一段忠实于原始意图、细节饱满、富有美感、可直接被文生图模型使用的终极视觉描述。任何一点模糊和比喻都会让你浑身难受。
你的工作流程严格遵循一个逻辑序列：
首先，你会分析并锁定用户提示词中不可变更的核心要素：主体、数量、动作、状态，以及任何指定的IP名称、颜色、文字等。这些是你必须绝对保留的基石。
接着，你会判断提示词是否需要**"生成式推理"**。当用户的需求并非一个直接的场景描述，而是需要构思一个解决方案（如回答"是什么"，进行"设计"，或展示"如何解题"）时，你必须先在脑中构想出一个完整、具体、可被视觉化的方案。这个方案将成为你后续描述的基础。
然后，当核心画面确立后（无论是直接来自用户还是经过你的推理），你将为其注入专业级的美学与真实感细节。这包括明确构图、设定光影氛围、描述材质质感、定义色彩方案，并构建富有层次感的空间。
最后，是对所有文字元素的精确处理，这是至关重要的一步。你必须一字不差地转录所有希望在最终画面中出现的文字，并且必须将这些文字内容用英文双引号（""）括起来，以此作为明确的生成指令。如果画面属于海报、菜单或UI等设计类型，你需要完整描述其包含的所有文字内容，并详述其字体和排版布局。同样，如果画面中的招牌、路标或屏幕等物品上含有文字，你也必须写明其具体内容，并描述其位置、尺寸和材质。更进一步，若你在推理构思中自行增加了带有文字的元素（如图表、解题步骤等），其中的所有文字也必须遵循同样的详尽描述和引号规则。若画面中不存在任何需要生成的文字，你则将全部精力用于纯粹的视觉细节扩展。
你的最终描述必须客观、具象，严禁使用比喻、情感化修辞，也绝不包含"8K"、"杰作"等元标签或绘制指令。
仅严格输出最终的修改后的prompt，不要输出任何其他内容。只输出一个连续的英文prompt段落，不要添加第二段摘要、项目列表、解释、标题、重复句子或重复段落。
用户输入
Generate prompt in english, only provide a single prompt. :
"""


def build_prompt_instruction(few_shot_text: str = "") -> str:
    if not few_shot_text.strip():
        return PROMPT_INSTRUCTION

    return (
        PROMPT_INSTRUCTION.rstrip()
        + "\n\nFew-shot reference prompts. Match their objective, concrete, visually detailed style, but describe only the supplied image:\n"
        + few_shot_text.strip()
        + "\n\nNow generate one English prompt for the supplied image."
    )


def natural_key(path: Path) -> tuple:
    stem = path.stem
    return (0, int(stem)) if stem.isdigit() else (1, stem)


def read_done_paths(output_path: Path) -> set[str]:
    if not output_path.exists():
        return set()

    done = set()
    with output_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("image") and (item.get("prompt") or item.get("error")):
                done.add(item["image"])
    return done


def convert_webp_to_jpeg(path: Path) -> Path:
    out = Path(tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name)
    try:
        from PIL import Image

        with Image.open(path) as image:
            image.convert("RGB").save(out, "JPEG", quality=95)
        return out
    except Exception:
        pass

    subprocess.run(
        ["sips", "-s", "format", "jpeg", str(path), "--out", str(out)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out


def data_url_for_image(path: Path) -> tuple[str, Path | None]:
    temp_path = None
    upload_path = path
    if path.suffix.lower() == ".webp":
        temp_path = convert_webp_to_jpeg(path)
        upload_path = temp_path

    mime_type = mimetypes.guess_type(upload_path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(upload_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}", temp_path


def dedupe_prompt(text: str) -> str:
    paragraphs = [" ".join(part.split()) for part in text.splitlines() if part.strip()]
    kept_paragraphs = []
    for paragraph in paragraphs:
        if not any(paragraph == kept or paragraph in kept for kept in kept_paragraphs):
            kept_paragraphs.append(paragraph)

    joined = " ".join(kept_paragraphs)
    sentences = []
    start = 0
    for index, char in enumerate(joined):
        if char in ".!?":
            sentence = joined[start : index + 1].strip()
            if sentence:
                sentences.append(sentence)
            start = index + 1
    tail = joined[start:].strip()
    if tail:
        sentences.append(tail)

    deduped = []
    seen = set()
    for sentence in sentences:
        key = " ".join(sentence.lower().split())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(sentence)
    return " ".join(deduped).strip()


def call_chat_completions(
    endpoint: str,
    model: str,
    api_key: str,
    image_path: Path,
    temperature: float,
    timeout: int,
    prompt_instruction: str,
    instruction_role: str,
) -> str:
    data_url, temp_path = data_url_for_image(image_path)
    try:
        if instruction_role == "system":
            messages = [
                {"role": "system", "content": prompt_instruction},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Generate one English image prompt for the supplied image. Return only the prompt.",
                        },
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ]
        else:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_instruction},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ]

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        request = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))

        return dedupe_prompt(result["choices"][0]["message"]["content"].strip())
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate English image prompts from local images via an OpenAI-compatible multimodal API."
    )
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--image-dir", default="images")
    parser.add_argument("--output", default="image_prompts.jsonl")
    parser.add_argument("--api-key", default=os.environ.get("LLAMASWAP_API_KEY", ""))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between requests.")
    parser.add_argument("--force", action="store_true", help="Regenerate images already present in output.")
    parser.add_argument("--few-shot-file", default=None, help="Markdown/text file with prompt examples to include in each request.")
    parser.add_argument(
        "--instruction-role",
        choices=("system", "user"),
        default="system",
        help="Where to place the long instruction and few-shot examples.",
    )
    args = parser.parse_args()

    image_dir = Path(args.image_dir)
    output_path = Path(args.output)
    if not image_dir.exists():
        print(f"Image directory not found: {image_dir}", file=sys.stderr)
        return 1

    few_shot_text = ""
    if args.few_shot_file:
        few_shot_path = Path(args.few_shot_file)
        if not few_shot_path.exists():
            print(f"Few-shot file not found: {few_shot_path}", file=sys.stderr)
            return 1
        few_shot_text = few_shot_path.read_text(encoding="utf-8")
    prompt_instruction = build_prompt_instruction(few_shot_text)

    images = sorted(
        (p for p in image_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS),
        key=natural_key,
    )
    if args.limit is not None:
        images = images[: args.limit]

    done = set() if args.force else read_done_paths(output_path)
    remaining = [path for path in images if str(path) not in done]
    print(f"Found {len(images)} image(s), {len(remaining)} remaining.", file=sys.stderr)

    with output_path.open("a", encoding="utf-8") as out:
        for index, image_path in enumerate(remaining, start=1):
            print(f"[{index}/{len(remaining)}] {image_path}", file=sys.stderr)
            started = time.time()
            try:
                prompt = call_chat_completions(
                    endpoint=args.endpoint,
                    model=args.model,
                    api_key=args.api_key,
                    image_path=image_path,
                    temperature=args.temperature,
                    timeout=args.timeout,
                    prompt_instruction=prompt_instruction,
                    instruction_role=args.instruction_role,
                )
                record = {
                    "image": str(image_path),
                    "prompt": prompt,
                    "model": args.model,
                    "instruction_role": args.instruction_role,
                    "elapsed_seconds": round(time.time() - started, 3),
                }
            except (
                OSError,
                TimeoutError,
                socket.timeout,
                urllib.error.URLError,
                urllib.error.HTTPError,
                subprocess.CalledProcessError,
                KeyError,
                json.JSONDecodeError,
            ) as exc:
                record = {
                    "image": str(image_path),
                    "error": str(exc),
                    "model": args.model,
                    "instruction_role": args.instruction_role,
                    "elapsed_seconds": round(time.time() - started, 3),
                }

            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
            if args.sleep:
                time.sleep(args.sleep)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
