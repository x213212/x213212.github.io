#!/usr/bin/env python3
"""Create a separate, curated English category layer for imported posts.

Categories intentionally live in data/categories.json rather than Markdown
front matter.  Original tags remain untouched and an override file makes every
automatic decision easy to review without editing article content.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    (
        "Security & Reverse Engineering",
        (
            "hacking", "reverse", "ida", "frida", "angr", "afl", "fuzz", "exploit", "cheat",
            "vulnerability", "static analyzer", "asan", "addresssanitizer", "double free", "heap",
            "sanitizer", "memleak", "memory leak", "malware",
        ),
    ),
    (
        "Systems & Low-Level",
        (
            "osdev", "operating system", "linux kernel", "kernel", "xv6", "qemu", "riscv", "riscv",
            "arm", "assembly", " asm", "gcc", "llvm", "compiler", "complier", "elf", "ebpf", " bpf",
            "dtrace", "virtio", "pthread", "valgrind", "gdb", "gdbserver", "callgraph", "cfg", "mmio",
            "binary", "linker", "inline", "unroll loop",
        ),
    ),
    (
        "Embedded & Hardware",
        (
            "arduino", "esp8266", "nodemcu", "rfid", "ir_remote", "ir remote", "jetson", "3d printer",
            "3d scanner", "embedded", "risc-v", "riscv", "ups", "nas", "raspberry", "sensor", "pcb",
        ),
    ),
    (
        "AI & Data",
        (
            "chatgpt", "llm", "llama", "graphrag", "pytorch", "tensorflow", "tesorflow", "lstm",
            "machine learning", "deep learning", "dify", "activeloop", "chatbot", "ai ", " ai",
        ),
    ),
    (
        "Finance & Blockchain",
        (
            "stock", "bitcoin", "bcoin", "geth", "ethereum", " eth", "blockchain", "crypto", "ganache",
            "trading", "finance", "wallet",
        ),
    ),
    (
        "Games & Multimedia",
        (
            "game_maker", "game maker", "gameboy", "gb_emu", "ffmpeg", "rtmp", "hls", "livego",
            "adobe media", "actionscript", "ghost cube", "emulator", "streaming", "video",
        ),
    ),
    (
        "DevOps & Infrastructure",
        (
            "devops", "docker", "kubernetes", "jenkins", "drone", "gitlab", "circleci", "ci/cd",
            "cicd", "nginx", "openresty", "server", "gcp", "auto scaling", "autodevops", "lab-net",
            "zipkin", "elk", "elasticsearch", "logstash", "kibana", "prometheus", "deploy", "deployment",
        ),
    ),
    (
        "Backend & Cloud",
        (
            "spring", "microservice", "redis", "rabbitmq", "kafka", "mysql", "mongodb", "oauth", "feign",
            "zuul", "hystrix", "mybatis", "flask", "api server", "websocket", "web socket", "rest",
            "distributed system", "loadbalance", "loadblance", "id generator", "java", "jave",
        ),
    ),
    (
        "Web & Frontend",
        (
            "vue", "html5", "nodejs", "node.js", "javascript", "typescript", "vscode extension", "css",
            "webassembly", "wasm", "websocket", "web socket", "react", "frontend", "front-end",
        ),
    ),
    (
        "Languages & Software Engineering",
        (
            "python", "golang", " rust", "rust ", "c#", " c ", "php", ".net", "vb6", "java", "jave",
            "erlang", "lua", "antlr", "algorithm", "data structure", "software", "programming", "nuitka",
        ),
    ),
    (
        "Life & Misc",
        ("life", "repair", "3d printer", "google map", "photos", "travel", "note", "分享"),
    ),
]


def normalized_haystack(post: dict) -> str:
    values = [post.get("title", ""), *post.get("tags", [])]
    return " ".join(str(value) for value in values).casefold().replace("_", " ")


def infer_categories(post: dict) -> tuple[list[str], dict[str, list[str]]]:
    haystack = normalized_haystack(post)
    found: list[str] = []
    evidence: dict[str, list[str]] = {}
    for category, terms in CATEGORY_RULES:
        matched = [term for term in terms if term in haystack]
        if matched:
            found.append(category)
            evidence[category] = matched
    if not found:
        found = ["General Technical Notes"]
        evidence["General Technical Notes"] = ["fallback"]
    return found[:3], evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    posts = json.loads((root / "data" / "posts.json").read_text(encoding="utf-8"))["posts"]
    overrides_path = root / "data" / "category-overrides.json"
    if not overrides_path.exists():
        overrides_path.write_text("{}\n", encoding="utf-8")
    overrides = json.loads(overrides_path.read_text(encoding="utf-8"))

    assignments: dict[str, list[str]] = {}
    evidence_by_route: dict[str, dict[str, list[str]]] = {}
    counts: Counter[str] = Counter()
    for post in posts:
        route = post["route"]
        if route in overrides:
            categories = list(dict.fromkeys(overrides[route]))
            evidence = {category: ["manual override"] for category in categories}
        else:
            categories, evidence = infer_categories(post)
        assignments[route] = categories
        evidence_by_route[route] = evidence
        counts.update(categories)

    output = {
        "schema_version": 1,
        "description": "Curated categories are independent from article Markdown and original Blogger tags.",
        "category_order": [name for name, _ in CATEGORY_RULES] + ["General Technical Notes"],
        "assignments": assignments,
        "evidence": evidence_by_route,
        "counts": dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))),
    }
    (root / "data" / "categories.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"posts": len(posts), "categories": dict(output["counts"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
