#!/usr/bin/env python3
"""Dependency-free structural audit for legacy HTML pages.

This is a triage tool, not a WCAG conformance checker. It reports observable
HTML patterns and intentionally avoids inferring accessibility conformance.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

DEPRECATED_TAGS = {
    "applet", "basefont", "big", "center", "font", "marquee", "nobr",
    "strike", "tt",
}


class _AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.doctype_present = False
        self.tag_counts: Counter[str] = Counter()
        self.deprecated_counts: Counter[str] = Counter()
        self.missing_img_alt = 0
        self.empty_img_alt = 0
        self.missing_area_alt = 0
        self.empty_area_alt = 0
        self.area_title_without_alt = 0
        self.missing_area_href = 0
        self.missing_area_coords = 0
        self.missing_html_lang = True
        self.viewport_meta = False
        self.map_ids: set[str] = set()
        self.usemap_refs: set[str] = set()
        self.heading_counts: Counter[str] = Counter()

    def handle_decl(self, decl: str) -> None:
        if decl.strip().lower().startswith("doctype html"):
            self.doctype_present = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._inspect_tag(tag.lower(), attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._inspect_tag(tag.lower(), attrs)

    def _inspect_tag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tag_counts[tag] += 1
        if tag in DEPRECATED_TAGS:
            self.deprecated_counts[tag] += 1

        values = {key.lower(): value for key, value in attrs}
        if tag == "html":
            self.missing_html_lang = not bool((values.get("lang") or "").strip())
        elif tag == "meta" and (values.get("name") or "").strip().lower() == "viewport":
            self.viewport_meta = True
        elif tag == "img":
            if "alt" not in values:
                self.missing_img_alt += 1
            elif not (values.get("alt") or "").strip():
                self.empty_img_alt += 1
            usemap = (values.get("usemap") or "").strip()
            if usemap.startswith("#") and len(usemap) > 1:
                self.usemap_refs.add(usemap[1:])
        elif tag == "map":
            # HTML 4 image maps commonly used `name`; modern markup uses `id`.
            for map_key in ("id", "name"):
                map_id = (values.get(map_key) or "").strip()
                if map_id:
                    self.map_ids.add(map_id)
        elif tag == "area":
            alt_value = values.get("alt")
            has_alt = "alt" in values
            if not has_alt:
                self.missing_area_alt += 1
            elif not (alt_value or "").strip():
                self.empty_area_alt += 1
            if not (alt_value or "").strip() and (values.get("title") or "").strip():
                self.area_title_without_alt += 1
            if not (values.get("href") or "").strip():
                self.missing_area_href += 1
            if not (values.get("coords") or "").strip():
                self.missing_area_coords += 1
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_counts[tag] += 1


def audit_html(source: str) -> dict[str, Any]:
    """Return structural observations for an HTML source string."""
    parser = _AuditParser()
    parser.feed(source)
    parser.close()
    total_areas = parser.tag_counts["area"]
    total_images = parser.tag_counts["img"]
    unmatched_usemap_refs = sorted(parser.usemap_refs - parser.map_ids)
    unreferenced_map_ids = sorted(parser.map_ids - parser.usemap_refs)
    return {
        "doctype_present": parser.doctype_present,
        "html_lang_missing": parser.missing_html_lang,
        "viewport_meta_present": parser.viewport_meta,
        "images": {
            "total": total_images,
            "missing_alt": parser.missing_img_alt,
            "empty_alt": parser.empty_img_alt,
        },
        "image_maps": {
            "map_count": parser.tag_counts["map"],
            "area_count": total_areas,
            "areas_missing_alt": parser.missing_area_alt,
            "areas_empty_alt": parser.empty_area_alt,
            "areas_with_title_but_no_alt": parser.area_title_without_alt,
            "areas_missing_href": parser.missing_area_href,
            "areas_missing_coords": parser.missing_area_coords,
            "usemap_references": sorted(parser.usemap_refs),
            "map_ids": sorted(parser.map_ids),
            "unmatched_usemap_references": unmatched_usemap_refs,
            "unreferenced_map_ids": unreferenced_map_ids,
        },
        "legacy_markup": {
            "counts": dict(sorted(parser.deprecated_counts.items())),
            "total": sum(parser.deprecated_counts.values()),
        },
        "frames": {
            "iframe": parser.tag_counts["iframe"],
            "frame": parser.tag_counts["frame"],
            "frameset": parser.tag_counts["frameset"],
        },
        "headings": dict(sorted(parser.heading_counts.items())),
        "tag_counts": dict(sorted(parser.tag_counts.items())),
        "scope_note": (
            "Structural triage only. Counts do not establish WCAG conformance, "
            "keyboard operability, screen-reader quality, or runtime behavior."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_file", type=Path, help="Path to a saved HTML file")
    parser.add_argument("--json", action="store_true", help="Print full JSON output")
    args = parser.parse_args()

    try:
        source = args.html_file.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        parser.error(f"cannot read {args.html_file}: {exc}")

    report = audit_html(source)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    maps = report["image_maps"]
    images = report["images"]
    print(f"HTML structural triage: {args.html_file}")
    print(f"DOCTYPE present: {report['doctype_present']}")
    print(f"HTML lang missing: {report['html_lang_missing']}")
    print(f"Viewport metadata present: {report['viewport_meta_present']}")
    print(f"Images: {images['total']} total; {images['missing_alt']} missing alt; {images['empty_alt']} empty alt")
    print(
        "Image maps: "
        f"{maps['map_count']} map(s); {maps['area_count']} area(s); "
        f"{maps['areas_missing_alt']} missing alt; "
        f"{maps['areas_empty_alt']} empty alt; "
        f"{maps['areas_missing_href']} missing href; "
        f"{maps['areas_missing_coords']} missing coords"
    )
    print(f"Legacy markup elements: {report['legacy_markup']['total']} {report['legacy_markup']['counts']}")
    print(f"Frames: {report['frames']}")
    print(report["scope_note"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
