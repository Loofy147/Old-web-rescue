import unittest

from legacy_html_audit import audit_html


class LegacyHtmlAuditTests(unittest.TestCase):
    def test_detects_missing_doctype_language_and_viewport(self):
        report = audit_html("<html><head></head><body></body></html>")
        self.assertFalse(report["doctype_present"])
        self.assertTrue(report["html_lang_missing"])
        self.assertFalse(report["viewport_meta_present"])

    def test_accepts_doctype_language_and_viewport(self):
        source = '<!DOCTYPE html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"></head></html>'
        report = audit_html(source)
        self.assertTrue(report["doctype_present"])
        self.assertFalse(report["html_lang_missing"])
        self.assertTrue(report["viewport_meta_present"])

    def test_counts_missing_and_empty_image_alt_separately(self):
        report = audit_html('<img src="a.png"><img src="b.png" alt=""><img src="c.png" alt="Dog">')
        self.assertEqual(report["images"], {"total": 3, "missing_alt": 1, "empty_alt": 1})

    def test_counts_area_alt_and_title_only_fallbacks(self):
        source = '<map id="m"><area href="a" coords="0,0,1,1" title="A"><area href="b" coords="0,0,1,1" alt=""><area href="c" coords="0,0,1,1" alt="C"></map>'
        maps = audit_html(source)["image_maps"]
        self.assertEqual(maps["area_count"], 3)
        self.assertEqual(maps["areas_missing_alt"], 1)
        self.assertEqual(maps["areas_empty_alt"], 1)
        self.assertEqual(maps["areas_with_title_but_no_alt"], 1)

    def test_detects_missing_area_href_and_coords(self):
        maps = audit_html('<map><area alt="A"><area alt="B" href="/b"></map>')["image_maps"]
        self.assertEqual(maps["areas_missing_href"], 1)
        self.assertEqual(maps["areas_missing_coords"], 2)

    def test_checks_usemap_references_against_map_ids(self):
        source = '<img src="a.png" usemap="#known"><map id="known"></map><img src="b.png" usemap="#missing"><map id="unused"></map>'
        maps = audit_html(source)["image_maps"]
        self.assertEqual(maps["unmatched_usemap_references"], ["missing"])
        self.assertEqual(maps["unreferenced_map_ids"], ["unused"])

    def test_supports_html4_map_name_without_map_id(self):
        report = audit_html('<img src="a.png" usemap="#legacy"><map name="legacy"><area href="/x" coords="0,0,1,1" alt="X"></map>')
        maps = report["image_maps"]
        self.assertEqual(maps["map_ids"], ["legacy"])
        self.assertEqual(maps["unmatched_usemap_references"], [])

    def test_counts_legacy_markup_and_frames(self):
        source = '<center><font>Old</font><nobr>Text</nobr><iframe></iframe><frameset><frame></frameset></center>'
        report = audit_html(source)
        self.assertEqual(report["legacy_markup"]["total"], 3)
        self.assertEqual(report["frames"], {"iframe": 1, "frame": 1, "frameset": 1})

    def test_counts_heading_levels(self):
        report = audit_html('<h1>A</h1><h2>B</h2><h2>C</h2><h4>D</h4>')
        self.assertEqual(report["headings"], {"h1": 1, "h2": 2, "h4": 1})

    def test_report_includes_non_conformance_scope_note(self):
        report = audit_html('<html lang="en"></html>')
        self.assertIn("do not establish WCAG conformance", report["scope_note"])


if __name__ == "__main__":
    unittest.main()
