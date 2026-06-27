#!/usr/bin/env python3
"""Scrape live interiorchick.nl product pages into page-html and update MDX frontmatter."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = ROOT / "src/content/pages"
HTML_DIR = ROOT / "src/data/page-html"
PUBLIC_IMAGES = ROOT / "public/images"
SITE_URL = "https://interiorchick.nl"
DEFAULT_IMAGE = "/images/2023/06/digitale-wekker.jpeg"

REMOVE_WIDGETS = {"table-of-contents", "social-icons", "spacer", "divider"}


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def upload_to_local(url: str) -> str:
    if not url:
        return url
    clean = url.split("?")[0]
    if "/wp-content/uploads/" in clean:
        rel = clean.split("/wp-content/uploads/", 1)[1]
        return f"/images/{rel}"
    return clean


def rewrite_urls(content: str) -> str:
    content = re.sub(
        rf"https?://(?:www\.)?interiorchick\.nl/wp-content/uploads/([^\s\"')]+)",
        r"/images/\1",
        content,
    )
    content = re.sub(
        rf"{re.escape(SITE_URL)}/(?P<slug>[a-z0-9\-_/]+)/?",
        r"/\g<slug>/",
        content,
    )
    content = re.sub(r"(/[^/\s\"')]+)/+", r"\1/", content)
    return content


def download_image(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["curl", "-sfL", "--max-time", "45", url, "-o", str(dest)],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and dest.exists() and dest.stat().st_size > 0


def fetch_html(slug: str) -> str | None:
    url = f"{SITE_URL}/{slug}/"
    result = subprocess.run(
        ["curl", "-sfL", "--max-time", "60", url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout


def widget_type(widget) -> str | None:
    for cls in widget.get("class", []):
        if cls.startswith("elementor-widget-") and cls not in {
            "elementor-widget",
            "elementor-widget-container",
        }:
            return cls.replace("elementor-widget-", "")
    return None


def clean_html(html: str) -> str:
    html = re.sub(r"\[[^\]]*\]", "", html)
    html = re.sub(r'data-type="[^"]*"', "", html)
    html = re.sub(r'data-word="[^"]*"', "", html)
    html = re.sub(r'title="Er is een mogelijke spelfout gevonden\."', "", html)
    return html


def extract_page(html: str) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")
    wp_page = soup.find(attrs={"data-elementor-type": "wp-page"})
    if not wp_page:
        return None

    meta_desc = soup.find("meta", attrs={"name": "description"})
    og_image = soup.find("meta", property="og:image")
    description = (
        meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""
    )
    featured_image = DEFAULT_IMAGE
    if og_image and og_image.get("content") and "wp-content/uploads" in og_image["content"]:
        featured_image = upload_to_local(og_image["content"])

    breadcrumb_widget = wp_page.select_one(".elementor-widget-breadcrumbs")
    if breadcrumb_widget:
        host = breadcrumb_widget.find_parent(
            "div", class_=lambda c: c and "elementor-element" in " ".join(c)
        )
        (host or breadcrumb_widget).decompose()

    for widget in wp_page.find_all(
        "div",
        class_=lambda c: c
        and "elementor-element" in " ".join(c)
        and "elementor-widget" in " ".join(c),
    ):
        if widget_type(widget) in REMOVE_WIDGETS:
            widget.decompose()

    for tag in wp_page.find_all(["script", "style", "iframe"]):
        tag.decompose()

    page_title = ""
    h1 = wp_page.find("h1")
    if h1:
        page_title = h1.get_text(" ", strip=True)

    body_html = rewrite_urls(wp_page.decode_contents())
    body_html = clean_html(body_html)

    if not page_title or len(body_html) < 200:
        return None

    return {
        "title": page_title,
        "description": description[:500] or f"Ontdek de beste {page_title.lower()} op InteriorChick.nl.",
        "featuredImage": featured_image,
        "content": body_html,
    }


def write_mdx(slug: str, data: dict) -> None:
    lines = [
        "---",
        f"title: {yaml_quote(data['title'])}",
        f"description: {yaml_quote(data['description'])}",
        f"featuredImage: {yaml_quote(data['featuredImage'])}",
        'pageType: "product"',
        "---",
        "",
    ]
    (PAGES_DIR / f"{slug}.mdx").write_text("\n".join(lines), encoding="utf-8")
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    (HTML_DIR / f"{slug}.html").write_text(data["content"], encoding="utf-8")


def collect_image_urls(content: str, featured: str) -> set[str]:
    urls: set[str] = set()
    if featured.startswith("/images/"):
        urls.add(f"{SITE_URL}/wp-content/uploads/{featured.removeprefix('/images/')}")
    for match in re.findall(r"/images/([^\s\"')]+)", content):
        urls.add(f"{SITE_URL}/wp-content/uploads/{match}")
    return urls


def scrape_slug(slug: str) -> tuple[str, bool, str]:
    html = fetch_html(slug)
    if not html:
        return slug, False, "fetch failed"
    data = extract_page(html)
    if not data:
        return slug, False, "extract failed"
    write_mdx(slug, data)
    urls = collect_image_urls(data["content"], data["featuredImage"])
    for url in urls:
        rel = url.split("/wp-content/uploads/", 1)[-1]
        download_image(url, PUBLIC_IMAGES / rel)
    return slug, True, f"{len(data['content'])} chars"


def main() -> int:
    slugs = sorted(p.stem for p in PAGES_DIR.glob("beste-*.mdx"))
    if not slugs:
        print("No product pages found")
        return 1

    print(f"Scraping {len(slugs)} product pages from {SITE_URL}...")
    ok = fail = 0
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(scrape_slug, slug): slug for slug in slugs}
        for future in as_completed(futures):
            slug, success, msg = future.result()
            if success:
                ok += 1
                print(f"  OK {slug}: {msg}")
            else:
                fail += 1
                print(f"  FAIL {slug}: {msg}", file=sys.stderr)

    print(f"Done: {ok} ok, {fail} failed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
