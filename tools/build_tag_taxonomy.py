#!/usr/bin/env python3
"""Build a display-only English topic merge for imported Blogger tags.

The source article data and Markdown are deliberately read-only here.  The
curated source map lives in ``data/tag-topic-map.json`` and exact corrections
can be made in ``data/tag-topic-overrides.json``.  The generated
``data/tag-taxonomy.json`` is designed for the static site's topic/word-cloud
UI while retaining every original Blogger label as a traceable member tag.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise SystemExit(f"tag taxonomy error: {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Validate mapping without writing output.")
    args = parser.parse_args()
    root = args.root.resolve()

    posts = read_json(root / "data" / "posts.json")["posts"]
    source = read_json(root / "data" / "tag-topic-map.json")
    overrides_source = read_json(root / "data" / "tag-topic-overrides.json")
    overrides = overrides_source.get("tag_overrides", overrides_source)
    if not isinstance(overrides, dict):
        fail("tag_overrides must be an object")

    raw_tag_counts = Counter(tag for post in posts for tag in post.get("tags", []))
    raw_tags = set(raw_tag_counts)
    topics = source.get("topics")
    if not isinstance(topics, list) or not topics:
        fail("tag-topic-map.json requires a non-empty topics list")

    topic_ids: set[str] = set()
    tag_to_topic: dict[str, str] = {}
    topic_metadata: dict[str, dict[str, Any]] = {}
    topic_order: list[str] = []

    for topic in topics:
        if not isinstance(topic, dict):
            fail("each topic must be an object")
        topic_id = topic.get("id")
        label = topic.get("label")
        if not isinstance(topic_id, str) or not topic_id:
            fail("every topic needs a non-empty id")
        if topic_id in topic_ids:
            fail(f"duplicate topic id: {topic_id}")
        if not isinstance(label, str) or not label:
            fail(f"topic {topic_id} needs a label")
        topic_ids.add(topic_id)
        topic_order.append(topic_id)
        topic_metadata[topic_id] = {
            "id": topic_id,
            "label": label,
            "description": str(topic.get("description", "")),
            "show_in_word_cloud": bool(topic.get("show_in_word_cloud", True)),
        }
        for raw_tag in topic.get("tags", []):
            if not isinstance(raw_tag, str) or not raw_tag:
                fail(f"topic {topic_id} has an invalid raw tag")
            if raw_tag in tag_to_topic:
                fail(f"raw tag is listed by more than one topic: {raw_tag}")
            tag_to_topic[raw_tag] = topic_id

    configured_tags = set(tag_to_topic)
    extra_tags = sorted(configured_tags - raw_tags, key=str.casefold)
    if extra_tags:
        fail("source map contains tags not present in posts.json: " + ", ".join(extra_tags))

    for raw_tag, topic_id in overrides.items():
        if raw_tag not in raw_tags:
            fail(f"override references a tag not present in posts.json: {raw_tag}")
        if topic_id not in topic_ids:
            fail(f"override for {raw_tag!r} references unknown topic id: {topic_id!r}")
        tag_to_topic[raw_tag] = topic_id

    unmapped_tags = sorted(raw_tags - set(tag_to_topic), key=str.casefold)
    if unmapped_tags:
        fail("unmapped raw Blogger tags: " + ", ".join(unmapped_tags))

    topic_tag_names: dict[str, list[str]] = defaultdict(list)
    for raw_tag, topic_id in tag_to_topic.items():
        topic_tag_names[topic_id].append(raw_tag)
    for names in topic_tag_names.values():
        names.sort(key=lambda tag: (-raw_tag_counts[tag], tag.casefold()))

    topic_routes: dict[str, set[str]] = defaultdict(set)
    for post in posts:
        for topic_id in {tag_to_topic[tag] for tag in post.get("tags", [])}:
            topic_routes[topic_id].add(post["route"])

    rendered_topics: list[dict[str, Any]] = []
    for topic_id in topic_order:
        raw_tag_names = topic_tag_names[topic_id]
        raw_tag_uses = sum(raw_tag_counts[tag] for tag in raw_tag_names)
        rendered = {
            **topic_metadata[topic_id],
            "post_count": len(topic_routes[topic_id]),
            "raw_tag_count": len(raw_tag_names),
            "raw_tag_uses": raw_tag_uses,
            "weight": len(topic_routes[topic_id]),
            "tags": [
                {"name": tag, "post_count": raw_tag_counts[tag]}
                for tag in raw_tag_names
            ],
        }
        rendered_topics.append(rendered)

    word_cloud_topics = [
        {
            "id": topic["id"],
            "label": topic["label"],
            "weight": topic["weight"],
            "post_count": topic["post_count"],
        }
        for topic in rendered_topics
        if topic["show_in_word_cloud"]
    ]

    output = {
        "schema_version": 1,
        "description": "Curated English topic merge for display and word-cloud navigation. Original Blogger labels and article Markdown are unchanged.",
        "source": {
            "map": "data/tag-topic-map.json",
            "overrides": "data/tag-topic-overrides.json",
        },
        "original_tag_count": len(raw_tags),
        "original_tag_assignments": sum(raw_tag_counts.values()),
        "topic_order": topic_order,
        "topics": rendered_topics,
        "word_cloud": {
            "weight_field": "post_count",
            "description": "Topic weight is the number of unique posts carrying one or more original tags mapped to that topic. Format labels are intentionally excluded.",
            "topics": word_cloud_topics,
        },
        "tag_to_topic": dict(sorted(tag_to_topic.items(), key=lambda item: item[0].casefold())),
        "unmapped_tags": [],
        "override_count": len(overrides),
    }

    if args.check:
        print(json.dumps({"valid": True, "topics": len(rendered_topics), "tags": len(raw_tags)}, ensure_ascii=False))
        return 0

    output_path = root / "data" / "tag-taxonomy.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "posts": len(posts),
                "raw_tags": len(raw_tags),
                "topics": [
                    {"label": item["label"], "posts": item["post_count"], "cloud": item["show_in_word_cloud"]}
                    for item in rendered_topics
                ],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
