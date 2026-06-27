#!/usr/bin/env python3
"""Fix blog featured images from live interiorchick.nl pages."""

from __future__ import annotations

import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "src/content/blog"
PUBLIC_IMAGES = ROOT / "public/images"
SITE_URL = "https://interiorchick.nl"
DEFAULT_IMAGE = "/images/2023/06/digitale-wekker.jpeg"


def upload_to_local(url: str) -> str:
    clean = url.split("?")[0]
    if "/wp-content/uploads/" in clean:
        rel = clean.split("/wp-content/uploads/", 1)[1]
        return f"/images/{rel}"
    return clean


def download_image(url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["curl", "-sfL", "--max-time", "45", url, "-o", str(dest)],
        capture_output=True,
    )


def fetch_html(slug: str) -> str | None:
    result = subprocess.run(
        ["curl", "-sfL", "--max-time", "60", f"{SITE_URL}/{slug}/"],
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def extract_featured(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    og = soup.find("meta", property="og:image")
    if og and og.get("content") and "wp-content/uploads" in og["content"]:
        return upload_to_local(og["content"])

    for img in soup.find_all("img", src=True):
        src = img["src"]
        if "wp-content/uploads" in src and "InteriorChick" not in src:
            return upload_to_local(src)
    return None


def update_mdx(path: Path, featured: str) -> None:
    text = path.read_text(encoding="utf-8")
    if featured.startswith("/images/"):
        rel = featured.removeprefix("/images/")
        download_image(f"{SITE_URL}/wp-content/uploads/{rel}", PUBLIC_IMAGES / rel)

    if re.search(r'^featuredImage:\s*', text, re.M):
        text = re.sub(
            r'^featuredImage:\s*.+$',
            f'featuredImage: {json.dumps(featured)}',
            text,
            count=1,
            flags=re.M,
        )
    else:
        text = text.replace("---\n", f'---\nfeaturedImage: "{featured}"\n', 1)
    path.write_text(text, encoding="utf-8")


def fix_slug(slug: str) -> tuple[str, bool]:
    path = BLOG_DIR / f"{slug}.mdx"
    if not path.exists():
        return slug, False
    text = path.read_text(encoding="utf-8")
    if DEFAULT_IMAGE not in text:
        return slug, True
    html = fetch_html(slug)
    if not html:
        return slug, False
    featured = extract_featured(html)
    if not featured or featured == DEFAULT_IMAGE:
        return slug, False
    update_mdx(path, featured)
    return slug, True


def main() -> None:
    slugs = []
    for path in BLOG_DIR.glob("*.mdx"):
        if DEFAULT_IMAGE in path.read_text(encoding="utf-8"):
            slugs.append(path.stem)

    print(f"Fixing featured images for {len(slugs)} blog posts...")
    ok = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fix_slug, slug): slug for slug in slugs}
        for future in as_completed(futures):
            slug, success = future.result()
            if success:
                ok += 1
                print(f"  OK {slug}")
            else:
                print(f"  SKIP {slug}")

    print(f"Updated {ok}/{len(slugs)} posts")


if __name__ == "__main__":
    main()
