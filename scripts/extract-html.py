#!/usr/bin/env python3
"""Extract HTML bodies from MDX files into page-html/ for set:html rendering."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_DIR = ROOT / "src/data/page-html"
CONTENT_DIRS = [ROOT / "src/content/blog", ROOT / "src/content/pages"]


def split_frontmatter(text: str) -> tuple[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        return "", text
    return match.group(1), match.group(2)


def main() -> None:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    count = 0

    for content_dir in CONTENT_DIRS:
        if not content_dir.exists():
            continue
        for path in content_dir.glob("*.mdx"):
            text = path.read_text(encoding="utf-8")
            frontmatter, body = split_frontmatter(text)
            body = body.strip()
            if not body:
                continue

            slug = path.stem
            (HTML_DIR / f"{slug}.html").write_text(body, encoding="utf-8")
            path.write_text(f"---\n{frontmatter}\n---\n", encoding="utf-8")
            count += 1

    print(f"Extracted HTML for {count} files into {HTML_DIR}")


if __name__ == "__main__":
    main()
