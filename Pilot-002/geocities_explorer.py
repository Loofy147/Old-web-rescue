#!/usr/bin/env python3
"""Search and inspect preserved GeoCities pages using the public Arquivo.pt API.

This tool only retrieves public archive metadata and links. It does not modify
archived content or attempt to execute the legacy pages it discovers.
"""

from __future__ import annotations

import argparse
import csv
import json
import io
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

API_ROOT = "https://arquivo.pt"
USER_AGENT = "OldWebRescueLab/0.2 (+https://arquivo.pt/api)"
DEFAULT_COLLECTION = "Geocities"
MAX_TEXT_API_ITEMS = 500
MAX_IMAGE_API_ITEMS = 200


class ArchiveAPIError(RuntimeError):
    """Raised when Arquivo.pt cannot return a usable API response."""


def build_api_url(endpoint: str, params: dict[str, Any]) -> str:
    """Build a deterministic API URL while preserving repeated/list values."""
    endpoint = endpoint.strip("/")
    if not endpoint or ".." in endpoint or "://" in endpoint:
        raise ValueError("endpoint must be a simple API path")
    pairs: list[tuple[str, str]] = []
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            pairs.extend((key, str(item)) for item in value)
        else:
            pairs.append((key, str(value)))
    return f"{API_ROOT}/{endpoint}?{urllib.parse.urlencode(pairs)}"


def _format_timestamp(value: Any) -> str:
    raw = str(value or "")
    try:
        return datetime.strptime(raw, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return raw or ""


def _first_text(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return str(value[0]) if value else ""
    return str(value or "")


def _validate_items_payload(payload: Any, items_key: str) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise ArchiveAPIError("Arquivo.pt returned a non-object response")
    if "error" in payload:
        raise ArchiveAPIError(str(payload["error"]))
    items = payload.get(items_key)
    if not isinstance(items, list):
        raise ArchiveAPIError(f"Arquivo.pt response is missing the {items_key} array")
    if not all(isinstance(item, dict) for item in items):
        raise ArchiveAPIError(f"Arquivo.pt returned an invalid item in {items_key}")
    return items


def normalize_page_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Map the Text Search API response into stable, readable page records."""
    source_items = _validate_items_payload(payload, "response_items")
    rows = []
    for item in source_items:
        rows.append(
            {
                "title": str(item.get("title") or "Untitled archived page"),
                "original_url": str(item.get("originalURL") or ""),
                "captured_at": _format_timestamp(item.get("tstamp")),
                "archive_url": str(item.get("linkToArchive") or ""),
                "no_frame_url": str(item.get("linkToNoFrame") or ""),
                "screenshot_url": str(item.get("linkToScreenshot") or ""),
                "content_length": item.get("contentLength"),
                "digest": str(item.get("digest") or ""),
                "snippet": str(item.get("snippet") or ""),
                "collection": _first_text(item.get("collection")),
                "mime_type": str(item.get("mimeType") or ""),
            }
        )
    return rows


def normalize_image_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Map the Image Search API response into stable image/page records."""
    source_items = _validate_items_payload(payload, "responseItems")
    rows = []
    for item in source_items:
        rows.append(
            {
                "page_title": str(item.get("pageTitle") or "Untitled archived page"),
                "page_url": str(item.get("pageURL") or ""),
                "page_captured_at": _format_timestamp(item.get("pageTstamp")),
                "page_archive_url": str(item.get("pageLinkToArchive") or ""),
                "image_source_url": str(item.get("imgSrc") or ""),
                "image_captured_at": _format_timestamp(item.get("imgTstamp")),
                "image_archive_url": str(item.get("imgLinkToArchive") or ""),
                "alt_text": list(item.get("imgAlt") or []),
                "image_title": list(item.get("imgTitle") or []),
                "width": item.get("imgWidth"),
                "height": item.get("imgHeight"),
                "mime_type": str(item.get("imgMimeType") or ""),
                "collections": list(item.get("collection") or []),
            }
        )
    return rows


@dataclass
class SearchResult:
    estimated_count: int
    items: list[dict[str, Any]]
    offset: int = 0
    source: str = ""


class ArquivoClient:
    """Small standard-library client for the official Arquivo.pt APIs."""

    def __init__(self, timeout: float = 20.0, collection: str | None = DEFAULT_COLLECTION):
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        self.timeout = timeout
        self.collection = collection

    @staticmethod
    def _validate_paging(limit: int, offset: int, maximum: int) -> None:
        if not 1 <= limit <= maximum:
            raise ValueError(f"limit must be between 1 and {maximum}")
        if offset < 0:
            raise ValueError("offset must be zero or greater")

    def _get_json(self, url: str) -> dict[str, Any]:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ArchiveAPIError(f"Could not reach Arquivo.pt: {exc}") from exc
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ArchiveAPIError("Arquivo.pt returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ArchiveAPIError("Arquivo.pt returned a non-object JSON response")
        if "error" in payload:
            raise ArchiveAPIError(str(payload["error"]))
        return payload

    def search_pages(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> SearchResult:
        self._validate_paging(limit, offset, MAX_TEXT_API_ITEMS)
        if not query.strip():
            raise ValueError("query cannot be empty")
        params: dict[str, Any] = {"q": query.strip(), "maxItems": limit, "offset": offset}
        if self.collection:
            params["collection"] = self.collection
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        payload = self._get_json(build_api_url("textsearch", params))
        rows = normalize_page_items(payload)
        return SearchResult(
            estimated_count=int(payload.get("estimated_nr_results") or 0),
            items=rows,
            offset=offset,
            source="textsearch",
        )

    def history(self, url: str, limit: int = 50, offset: int = 0) -> SearchResult:
        self._validate_paging(limit, offset, MAX_TEXT_API_ITEMS)
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("history URL must be a complete http or https URL")
        payload = self._get_json(
            build_api_url("textsearch", {"versionHistory": url, "maxItems": limit, "offset": offset})
        )
        rows = normalize_page_items(payload)
        return SearchResult(
            estimated_count=int(payload.get("estimated_nr_results") or 0),
            items=rows,
            offset=offset,
            source="versionHistory",
        )

    def search_images(self, query: str, limit: int = 10, offset: int = 0) -> SearchResult:
        self._validate_paging(limit, offset, MAX_IMAGE_API_ITEMS)
        if not query.strip():
            raise ValueError("query cannot be empty")
        params: dict[str, Any] = {"q": query.strip(), "maxItems": limit, "offset": offset}
        if self.collection:
            params["collection"] = self.collection
        payload = self._get_json(build_api_url("imagesearch", params))
        rows = normalize_image_items(payload)
        return SearchResult(
            estimated_count=int(payload.get("totalItems") or 0),
            items=rows,
            offset=offset,
            source="imagesearch",
        )


def format_csv(rows: Iterable[dict[str, Any]]) -> str:
    rows = list(rows)
    if not rows:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()), extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value for key, value in row.items()})
    return output.getvalue()


def format_table(rows: list[dict[str, Any]], columns: list[tuple[str, str]], width: int = 100) -> str:
    if not rows:
        return "No results."
    pieces = []
    for row in rows:
        lines = []
        for key, label in columns:
            value = row.get(key, "")
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            value = str(value or "")
            lines.append(f"{label}: {textwrap.shorten(value, width=width, placeholder='…') if value else '—'}")
        pieces.append("\n".join(lines))
    return "\n\n".join(pieces)


def _write_result(args: argparse.Namespace, result: SearchResult, mode: str) -> None:
    envelope = {
        "source": result.source,
        "estimated_count": result.estimated_count,
        "offset": result.offset,
        "returned_count": len(result.items),
        "items": result.items,
    }
    if args.format == "json":
        content = json.dumps(envelope, ensure_ascii=False, indent=2)
    elif args.format == "csv":
        content = format_csv(result.items)
    else:
        if mode == "images":
            columns = [("page_title", "Page"), ("page_captured_at", "Page capture"), ("image_captured_at", "Image capture"), ("alt_text", "Alt"), ("image_archive_url", "Archived image"), ("page_archive_url", "Archived page")]
        else:
            columns = [("title", "Title"), ("captured_at", "Captured"), ("original_url", "Original URL"), ("archive_url", "Archived page"), ("snippet", "Snippet")]
        content = f"Estimated matches: {result.estimated_count}\nReturned: {len(result.items)} (offset {result.offset})\n\n" + format_table(result.items, columns)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"Saved {len(result.items)} records to {output_path}")
    else:
        print(content)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Search archived GeoCities pages and images via the public Arquivo.pt APIs."
    )
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds (default: 20)")
    parser.add_argument("--all-collections", action="store_true", help="Search all Arquivo.pt collections, not only GeoCities")
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", help="Search the text and metadata of archived pages")
    search.add_argument("query")
    _add_result_options(search, default_limit=10)
    search.add_argument("--from-date", help="Start capture date (YYYYMMDD or YYYYMMDDHHMMSS)")
    search.add_argument("--to-date", help="End capture date (YYYYMMDD or YYYYMMDDHHMMSS)")

    history = sub.add_parser("history", help="List archived captures of one original URL")
    history.add_argument("url")
    _add_result_options(history, default_limit=50)

    images = sub.add_parser("images", help="Search archived images and their source pages")
    images.add_argument("query")
    _add_result_options(images, default_limit=10)
    return parser


def _add_result_options(parser: argparse.ArgumentParser, default_limit: int) -> None:
    parser.add_argument("--limit", type=int, default=default_limit, help="Number of results (max 500 for pages, 200 for images)")
    parser.add_argument("--offset", type=int, default=0, help="Result offset for pagination")
    parser.add_argument("--format", choices=("table", "csv", "json"), default="table")
    parser.add_argument("--output", help="Write results to a file instead of stdout")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    client = ArquivoClient(timeout=args.timeout, collection=None if args.all_collections else DEFAULT_COLLECTION)
    try:
        if args.command == "search":
            result = client.search_pages(args.query, args.limit, args.offset, args.from_date, args.to_date)
        elif args.command == "history":
            result = client.history(args.url, args.limit, args.offset)
        else:
            result = client.search_images(args.query, args.limit, args.offset)
        _write_result(args, result, args.command)
        return 0
    except (ArchiveAPIError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
