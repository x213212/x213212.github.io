#!/usr/bin/env python3
"""A Python-Markdown extension for the HackMD syntax used by these posts.

The archive was written in HackMD, so posts contain a few constructs that plain
Markdown does not define. Handling them at render time keeps ``content/posts``
pure Markdown - the source stays editable in HackMD or any other editor, and the
site is what knows how to draw them.

Supported:

``:::info`` / ``success`` / ``warning`` / ``danger``
    Coloured callout blocks, rendered as ``<div class="callout callout--info">``.
``:::spoiler Title``
    A collapsed ``<details>`` block.
``~~text~~``
    Strikethrough, rendered as ``<del>``.
``- [ ]`` / ``- [x]``
    Task lists, rendered as disabled checkboxes.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as etree

from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import SimpleTagInlineProcessor
from markdown.treeprocessors import Treeprocessor

CALLOUT_KINDS = ("info", "success", "warning", "danger", "tip", "note")
CONTAINER_START = re.compile(r"(?m)^:::[ \t]*(?P<kind>[A-Za-z]+)[ \t]*(?P<title>[^\n]*)$")
CONTAINER_END = re.compile(r"(?m)^:::[ \t]*$")
STRIKETHROUGH = r"(~{2})(.+?)\1"
TASK_ITEM = re.compile(r"^\[(?P<state>[ xX])\][ \t]+(?P<rest>.*)$", re.DOTALL)


class ContainerProcessor(BlockProcessor):
    """Turn ``:::kind ... :::`` fences into callouts and spoilers."""

    def test(self, parent: etree.Element, block: str) -> bool:
        return bool(CONTAINER_START.match(block))

    def run(self, parent: etree.Element, blocks: list[str]) -> bool:
        opening = CONTAINER_START.match(blocks[0])
        kind = opening.group("kind").lower()
        if kind not in CALLOUT_KINDS and kind != "spoiler":
            return False

        title = opening.group("title").strip()
        blocks[0] = blocks[0][opening.end() :].lstrip("\n")

        collected: list[str] = []
        for index, block in enumerate(blocks):
            end = CONTAINER_END.search(block)
            if end is None:
                collected.append(block)
                continue
            collected.append(block[: end.start()])
            remainder = block[end.end() :].lstrip("\n")
            del blocks[: index + 1]
            if remainder:
                blocks.insert(0, remainder)
            break
        else:
            # Unterminated container: treat the rest of the document as content
            # rather than dropping it.
            blocks.clear()

        if kind == "spoiler":
            container = etree.SubElement(parent, "details")
            container.set("class", "spoiler")
            summary = etree.SubElement(container, "summary")
            summary.text = title or "Show more"
        else:
            container = etree.SubElement(parent, "div")
            container.set("class", f"callout callout--{kind}")
            if title:
                heading = etree.SubElement(container, "p")
                heading.set("class", "callout__title")
                heading.text = title

        self.parser.parseBlocks(container, [block for block in collected if block.strip()])
        return True


class TaskListProcessor(Treeprocessor):
    """Render ``- [ ]`` / ``- [x]`` items as read-only checkboxes."""

    def run(self, root: etree.Element) -> None:
        for parent in root.iter():
            if parent.tag not in {"ul", "ol"}:
                continue
            for item in parent:
                if item.tag != "li" or not item.text:
                    continue
                match = TASK_ITEM.match(item.text)
                if not match:
                    continue
                parent.set("class", "task-list")
                item.set("class", "task-list__item")
                checkbox = etree.Element("input")
                checkbox.set("type", "checkbox")
                checkbox.set("disabled", "disabled")
                if match.group("state").lower() == "x":
                    checkbox.set("checked", "checked")
                item.insert(0, checkbox)
                checkbox.tail = " " + match.group("rest")
                item.text = ""


class HackMDExtension(Extension):
    def extendMarkdown(self, md) -> None:  # noqa: N802 - Python-Markdown API
        md.parser.blockprocessors.register(ContainerProcessor(md.parser), "hackmd-container", 105)
        md.inlinePatterns.register(
            SimpleTagInlineProcessor(STRIKETHROUGH, "del"), "hackmd-strikethrough", 65
        )
        md.treeprocessors.register(TaskListProcessor(md), "hackmd-tasklist", 5)


def makeExtension(**kwargs):  # noqa: N802 - Python-Markdown API
    return HackMDExtension(**kwargs)
