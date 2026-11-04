import csv
import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from geocities_explorer import (
    ArchiveAPIError,
    ArquivoClient,
    build_api_url,
    format_csv,
    normalize_page_items,
)


class BuildApiUrlTests(unittest.TestCase):
    def test_search_url_encodes_terms_and_applies_geocities_collection(self):
        url = build_api_url(
            "textsearch",
            {"q": "personal diary", "maxItems": 5, "offset": 10, "collection": "Geocities"},
        )
        self.assertIn("q=personal+diary", url)
        self.assertIn("collection=Geocities", url)
        self.assertIn("maxItems=5", url)
        self.assertIn("offset=10", url)

    def test_version_history_url_uses_version_history_parameter(self):
        url = build_api_url(
            "textsearch",
            {"versionHistory": "https://geocities.com/kreisler76/diary.html", "maxItems": 20},
        )
        self.assertIn("versionHistory=https%3A%2F%2Fgeocities.com%2Fkreisler76%2Fdiary.html", url)


class ResponseNormalizationTests(unittest.TestCase):
    def test_normalizes_page_results_without_losing_capture_metadata(self):
        payload = {
            "estimated_nr_results": 6035,
            "response_items": [
                {
                    "title": "My Personal Diary",
                    "originalURL": "https://geocities.com/kreisler76/diary.html",
                    "linkToArchive": "https://arquivo.pt/wayback/20090427031225/https://geocities.com/kreisler76/diary.html",
                    "linkToNoFrame": "https://arquivo.pt/noFrame/replay/20090427031225/https://geocities.com/kreisler76/diary.html",
                    "tstamp": "20090427031225",
                    "snippet": "A personal diary page",
                    "collection": "Geocities",
                }
            ],
        }
        self.assertEqual(normalize_page_items(payload)[0]["captured_at"], "2009-04-27 03:12:25")
        self.assertEqual(normalize_page_items(payload)[0]["archive_url"], payload["response_items"][0]["linkToArchive"])
        self.assertIn("/noFrame/replay/", normalize_page_items(payload)[0]["no_frame_url"])

    def test_empty_search_response_is_valid(self):
        self.assertEqual(normalize_page_items({"estimated_nr_results": 0, "response_items": []}), [])

    def test_invalid_api_payload_raises_domain_error(self):
        with self.assertRaises(ArchiveAPIError):
            normalize_page_items({"error": "service unavailable"})


class ClientTests(unittest.TestCase):
    @patch("geocities_explorer.urllib.request.urlopen")
    def test_search_pages_calls_api_and_returns_normalized_records(self, mock_urlopen):
        response_payload = {
            "estimated_nr_results": 6035,
            "response_items": [
                {
                    "title": "My Personal Diary",
                    "originalURL": "https://geocities.com/kreisler76/diary.html",
                    "linkToArchive": "https://arquivo.pt/wayback/20090427031225/https://geocities.com/kreisler76/diary.html",
                    "tstamp": "20090427031225",
                    "snippet": "Cats came to visit the diary",
                    "collection": "Geocities",
                }
            ],
        }
        mock_response = io.BytesIO(json.dumps(response_payload).encode("utf-8"))
        mock_response.__enter__ = lambda self: self
        mock_response.__exit__ = lambda *args: None
        mock_urlopen.return_value = mock_response

        result = ArquivoClient().search_pages("personal diary", limit=5)
        self.assertEqual(result.estimated_count, 6035)
        self.assertEqual(result.items[0]["title"], "My Personal Diary")
        self.assertIn("collection=Geocities", mock_urlopen.call_args.args[0].full_url)

    @patch("geocities_explorer.urllib.request.urlopen")
    def test_history_uses_exact_url_version_history_request(self, mock_urlopen):
        response_payload = {
            "estimated_nr_results": 1,
            "response_items": [
                {
                    "title": "http://www.geocities.com/example/home.html",
                    "originalURL": "http://www.geocities.com/example/home.html",
                    "linkToArchive": "https://arquivo.pt/wayback/20090427031225/http://www.geocities.com/example/home.html",
                    "tstamp": "20090427031225",
                    "collection": "Geocities",
                }
            ],
        }
        mock_response = io.BytesIO(json.dumps(response_payload).encode("utf-8"))
        mock_response.__enter__ = lambda self: self
        mock_response.__exit__ = lambda *args: None
        mock_urlopen.return_value = mock_response

        result = ArquivoClient().history("http://www.geocities.com/example/home.html")
        request_url = mock_urlopen.call_args.args[0].full_url
        self.assertIn("versionHistory=http%3A%2F%2Fwww.geocities.com%2Fexample%2Fhome.html", request_url)
        self.assertEqual(result.items[0]["captured_at"], "2009-04-27 03:12:25")

    @patch("geocities_explorer.urllib.request.urlopen")
    def test_image_search_maps_image_and_page_archive_links(self, mock_urlopen):
        payload = {
            "totalItems": 51537,
            "responseItems": [
                {
                    "imgSrc": "http://example.org/dog.gif",
                    "imgLinkToArchive": "https://arquivo.pt/wayback/20090711063415im_/http://example.org/dog.gif",
                    "pageLinkToArchive": "https://arquivo.pt/wayback/20090624024559/http://example.org/page.html",
                    "pageTitle": "Dogs",
                    "imgAlt": ["Dog illustration"],
                    "imgTstamp": "20090711063415",
                    "collection": ["Geocities"],
                }
            ],
        }
        mock_response = io.BytesIO(json.dumps(payload).encode("utf-8"))
        mock_response.__enter__ = lambda self: self
        mock_response.__exit__ = lambda *args: None
        mock_urlopen.return_value = mock_response

        result = ArquivoClient().search_images("dogs", limit=5)
        self.assertEqual(result.estimated_count, 51537)
        self.assertEqual(result.items[0]["page_title"], "Dogs")
        self.assertEqual(result.items[0]["alt_text"], ["Dog illustration"])

    def test_page_search_rejects_more_than_text_api_maximum(self):
        with self.assertRaises(ValueError):
            ArquivoClient().search_pages("test", limit=501)

    def test_image_search_rejects_more_than_image_api_maximum(self):
        with self.assertRaises(ValueError):
            ArquivoClient().search_images("test", limit=201)

    @patch("geocities_explorer.urllib.request.urlopen")
    def test_api_transport_error_is_reported_cleanly(self, mock_urlopen):
        mock_urlopen.side_effect = OSError("offline")
        with self.assertRaises(ArchiveAPIError):
            ArquivoClient().search_pages("computers")


class CsvTests(unittest.TestCase):
    def test_live_sample_fixture_has_geocities_queries_and_capture_links(self):
        fixture_path = Path(__file__).parents[1] / "fixtures" / "live-sample.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertEqual(fixture["collection"], "Geocities")
        self.assertEqual(fixture["retrieved_on"], "2026-11-03")
        self.assertEqual(fixture["text_search_observations"][0]["estimated_nr_results"], 6035)
        self.assertIn("/noFrame/replay/", fixture["text_search_observations"][0]["sample"]["linkToNoFrame"])

    def test_csv_contains_normalized_columns_and_values(self):
        rows = [{"title": "My Personal Diary", "original_url": "https://example.org", "captured_at": "2009-04-27 03:12:25", "archive_url": "https://archive.org/x", "snippet": "hello"}]
        result = list(csv.DictReader(io.StringIO(format_csv(rows))))
        self.assertEqual(result[0]["title"], "My Personal Diary")
        self.assertEqual(result[0]["captured_at"], "2009-04-27 03:12:25")


if __name__ == "__main__":
    unittest.main()
