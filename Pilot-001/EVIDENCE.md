# Old Web Rescue Lab — Evidence Register

**Run date:** 2026-11-03  
**Run ID:** OWRL-P001  
**Scope:** task-based exploration of long-lived websites, historical snapshots, usability, accessibility barriers and technical condition.

## Method

- Inspected live pages and archived snapshots at desktop and mobile viewports.
- Followed information and reading journeys instead of treating a homepage screenshot as a full audit.
- Inspected source markup where behavior suggested a legacy dependency or accessibility issue.
- Ran the W3C Nu HTML Checker against representative documents.
- Separated observations from interpretation. Blocked or unavailable steps remain `UNKNOWN`.

## Findings

### CERN — original World Wide Web project page

**Journey:** project overview → information directory → help → software products → technical references → history → getting code.

- **ESTABLISHED:** The page exposes a compact documentation structure with links for FAQs, history, people, technical details, software products and obtaining source code. Source: https://info.cern.ch/hypertext/WWW/TheProject.html
- **EXPERIMENTALLY_SUPPORTED:** The text-first page reflowed at a 390 px viewport without obvious horizontal overflow in the captured browser view.
- **ESTABLISHED:** Nu HTML Checker reported 10 errors and 26 warnings. The report includes undeclared character encoding, absent doctype, obsolete `nextid`, invalid document structure and missing `lang`. Report: https://validator.w3.org/nu/?doc=https%3A%2F%2Finfo.cern.ch%2Fhypertext%2FWWW%2FTheProject.html
- **INFERENCE:** The information architecture remains useful despite obsolete markup and an unstyled presentation.
- **UNKNOWN:** Screen-reader behavior, keyboard order, link-rot rate and server-side security were not audited.

### Space Jam 1996 — preserved promotional site

**Journey:** site map → Junior Jam → Concentration → Match the Monstars → trivia.

- **ESTABLISHED:** The Concentration page tells visitors that the game requires the Shockwave plug-in and embeds `../../med/concentration.dcr`. Source: https://www.spacejam.com/1996/cmp/junior/concentration.html
- **EXPERIMENTALLY_SUPPORTED:** The current capture showed the game area empty; the text and page shell remained visible. This is consistent with the legacy plug-in dependency, but does not prove every possible browser setup fails.
- **ESTABLISHED:** Nu HTML Checker reported 18 errors and 24 warnings for the Junior Jam games page. Errors include missing doctype, obsolete presentational elements and two images without `alt` attributes. Report: https://validator.w3.org/nu/?doc=https%3A%2F%2Fwww.spacejam.com%2F1996%2Fcmp%2Fjunior%2Fgames.html
- **ESTABLISHED:** `match.html` has image links with text alternatives such as NULL, ZILCH, VOID, NADA and BUPKUS. Source: https://www.spacejam.com/1996/cmp/junior/match.html
- **INFERENCE:** The content and interaction idea have outlived the original game technology.
- **Action:** built an independent, offline memory-game prototype that removes the plug-in dependency and adds semantic buttons, keyboard access, readable state labels and live status announcements.
- **UNKNOWN:** Original Shockwave binary behavior, historical game completion path and full screen-reader compatibility were not reproduced.

### Internet Archive / Wayback Machine — preservation and retrieval

**Journey:** query a known historic URL → inspect capture timeline → open an archived capture.

- **ESTABLISHED:** The Wayback page for `info.cern.ch` reported 3,651 captures between 10 December 1997 and 27 October 2026 during this run. Calendar: https://web.archive.org/web/*/http://info.cern.ch/
- **Qualification:** The 10 December 1997 capture opened was a CERN HTTP daemon error page, not the original first-web-site homepage.
- **ESTABLISHED:** A 4 November 1999 capture says the original hypertext/WWW information was no longer available on the `info.cern.ch` server and that the physical machine no longer existed. Capture: https://web.archive.org/web/19991104103529/http://info.cern.ch/
- **INFERENCE:** Wayback is useful for preserving evidence of both content and disappearance; a capture date must not be mistaken for a successful capture of intended content.

### Project Gutenberg — discovery, reading and download

**Journey:** search “Pride and Prejudice” → open eBook record → read online → inspect alternative formats.

- **ESTABLISHED:** The inspected search returned 11 catalogue entries, with eBook 1342 (Jane Austen) first in the popularity-sorted results. Search: https://www.gutenberg.org/ebooks/search/?query=pride+and+prejudice
- **ESTABLISHED:** The book record exposes a direct online-reading route and multiple downloadable formats. Record: https://www.gutenberg.org/ebooks/1342
- **ESTABLISHED:** The eBook record provides EPUB3, older EPUB formats, Kindle formats, HTML ZIP and plain text choices. Record: https://www.gutenberg.org/ebooks/1342
- **EXPERIMENTALLY_SUPPORTED:** The book text and chapter navigation loaded in the inspected mobile view.
- **INFERENCE:** This is a strong example of format choice and long-term content portability.
- **UNKNOWN:** Screen-reader testing, download checksum verification and the full e-reader handoff flow were not tested. The book page advises users outside the United States to check local copyright law before reuse.

### W3C — current standards and validation workflow

- **ESTABLISHED:** W3C's WCAG 2.2 is labelled a W3C Recommendation dated 12 December 2024. Standard: https://www.w3.org/TR/WCAG22/
- **ESTABLISHED:** The current W3C homepage includes a skip-to-content link and a responsive mobile layout. Homepage: https://www.w3.org/
- **ESTABLISHED:** Nu HTML Checker reported zero errors and one warning for the W3C homepage. Report: https://validator.w3.org/nu/?doc=https%3A%2F%2Fwww.w3.org%2F
- **Qualification:** Standards and validation material are findable, but the validator checks markup conformance, not full accessibility conformance.

### Craigslist — task-focused marketplace

**Journey:** choose location → search computers → browse listings → open a listing.

- **EXPERIMENTALLY_SUPPORTED:** The inspected Atlanta computer search returned 329 results at that moment, with filter controls, sort order and list/grid/map presentation choices. Search: https://www.craigslist.org/search/area/atlanta?cat=sya
- **EXPERIMENTALLY_SUPPORTED:** Mobile and desktop captures showed different-density layouts; the mobile view retained search controls and listing cards.
- **ESTABLISHED:** Nu HTML Checker reported zero errors and one warning for the inspected search page; the warning was absence of an `html lang` attribute.
- **INFERENCE:** The marketplace remains task-efficient because category, location, filters and listing details are prioritized over decorative UI.
- **UNKNOWN:** Seller contact, posting, payment and fraud-reporting flows were not completed.

### Google — search interface evolution

- **ESTABLISHED:** The inspected mobile homepage exposed text entry alongside camera, microphone and AI Mode controls. Homepage: https://www.google.com/
- **EXPERIMENTALLY_SUPPORTED:** A test query `site:info.cern.ch "Getting code"` produced a captured results page whose surfaced results did not clearly match the query.
- **UNKNOWN:** The mismatch may be affected by location, ranking, personalization or capture behavior. This single run is insufficient to rate Google search relevance.

### Slashdot — news and community workflow

- **ESTABLISHED:** The inspected story contains a timestamp, topic links, source links and article text. Story: https://news.slashdot.org/story/26/11/03/214205/firefoxs-new-mini-window-is-every-multitaskers-dream
- **EXPERIMENTALLY_SUPPORTED:** In the captured mobile viewport, overlapping promotional content and a fixed bottom advertisement occupied a large share of the screen and obscured part of the story view. This is a session-specific observation, not a site-wide measurement.
- **UNKNOWN:** Full comment submission, moderation, reader settings and ad-dismissal persistence were not tested.

### Zombo.com — domain and content continuity

- **ESTABLISHED:** The current homepage says the domain was purchased via GoDaddy, that current content is new and unique, and that the new operators would like to purchase rights to the former site's content. Live page: https://zombo.com/
- **ESTABLISHED:** The Wayback calendar reported 7,241 captures between 28 November 1999 and 1 November 2026. Calendar: https://web.archive.org/web/*/http://zombo.com/
- **INFERENCE:** Domain continuity does not guarantee content continuity.

### Textfiles.com — text archive and BBS history

- **ESTABLISHED:** The archived BBS directory organizes text files with filename, size and description columns. Capture: https://web.archive.org/web/20010624153533/http://www.textfiles.com/bbs/
- **EXPERIMENTALLY_SUPPORTED:** At 390 px, introductory prose wraps, while the three-column directory table becomes cramped.
- **ESTABLISHED:** A representative plain-text file remains readable in a monospaced layout, but trailing SUB control characters are visible in replay. Capture: https://web.archive.org/web/20010724080517/http://www.textfiles.com/bbs/12budord.txt
- **INFERENCE:** A modern reader should preserve original bytes and expose a separate cleaned display mode rather than silently changing archived material.

### GeoCities — personal web pages

- **ESTABLISHED:** Arquivo.pt search can discover captured personal pages, diaries, tutorial pages and art portfolios in the GeoCities collection.
- **EXPERIMENTALLY_SUPPORTED:** The personal diary reflowed at 390 px; the How Computers Work page was clipped horizontally; the dog gallery's table-based image/text rows compressed descriptions into narrow columns.
- **UNKNOWN:** Full original site completeness, all scripts/assets and all screen-reader behaviors were not tested.

### Million Dollar Homepage — image-map discovery

- **ESTABLISHED:** Direct parse of the served homepage HTML found 251 `<area>` hotspots, all lacking `alt`; 80 hotspots had the `wayback-replaced` class and preserved their original target in `data-original-url`.
- **Qualification:** The served source comment claimed 1,164 replacements, but only 80 rewritten image-map hotspots were directly verified in the inspected homepage response. The wider claim remains unverified.
- **UNKNOWN:** Keyboard behavior, screen-reader naming, mobile hotspot usability and destination health were not tested.

## Cross-site conclusions

1. A long-lived site can be useful without being visually modern; task completion and information architecture matter more than decorative novelty.
2. Historical archive captures, page replays, extracted text, screenshots and original files are distinct evidence artifacts.
3. Mobile failure often comes from fixed-width image and table composition, not merely the site's age.
4. Plugin dependency can make a specific interaction unavailable even while its surrounding content survives.
5. HTML validation, structural triage and screenshots are not substitutes for complete human accessibility evaluation.

## Prototype

**Memory Reboot** implements the generic reveal/compare/match interaction independently of Space Jam's protected characters, artwork, music, code and branding. It is offline, uses native buttons, keyboard input, live status messages, reduced-motion styles and responsive layouts.

Run:
- `node --test game-engine.test.mjs`
- `python browser-smoke.py` (optional; Playwright + Chromium required)

## Limitations

- No human participants or assistive-technology users were involved.
- No formal screen-reader walkthrough was completed.
- No full security review or comprehensive link-health crawl was run.
- Archive replay can fail to load a dependency even if that dependency existed on the original site.
- Search result counts and ranking are time-sensitive estimates.
