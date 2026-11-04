# Field Notes — GeoCities Research Wave

**Inspection date:** 2026-11-03  
**Archive:** Arquivo.pt GeoCities collection  
**Device widths:** 390 px mobile; 1280 px desktop captures  
**Status:** Exploratory, task-based inspection; not a WCAG conformance audit.

## 1. Discovery surface

The GeoCities-specific search page is a lightweight entry point: one query field, English/Portuguese switch, and a search action. Its inline search function sends the query to `https://arquivo.pt/search.jsp` and appends `collection:Geocities`. The results interface provides page/image search, date-range controls, and export options.

The official Text Search API supports the equivalent collection restriction as a separate `collection=Geocities` parameter. The Explorer uses the API form, not the page's query-syntax shortcut.

### Live query observations

These counts are API/UI estimates observed on 2026-11-03 and are not stable inventory totals.

| Query | Estimated matching pages | First representative result |
|---|---:|---|
| `personal diary` | 6,035 | My Personal Diary — 2009-04-27 |
| `computers` | 50,659 | Welcome to How Computers Work — 2009-10-27 |
| `music` | 371,561 | Music History Resources — 2009-04-27 |
| `dogs` | 86,010 | Dogs, Dogs, Dogs — 2009-11-15 |
| `fan` | 144,330 | Fan Media — 2009-10-27 |
| Images: `dogs` | 51,537 | Mixed preserved image results; collection metadata includes GeoCities |

Counts are search-engine estimates; result coverage and rankings can change. A hit is not proof that every asset or outgoing link was preserved.

## 2. Page: My Personal Diary

**Archive capture:** 2009-04-27 03:12:25 UTC  
**Original page:** `https://geocities.com/kreisler76/diary.html`  
**Archived replay:** `https://arquivo.pt/noFrame/replay/20090427031225/https://geocities.com/kreisler76/diary.html`

### Journey

Search `personal diary` → open the first GeoCities result → view the replay page → inspect the preserved page's links and content.

### Observed behavior

- The capture is legible at 390 px and wraps into a single narrow column.
- The page preserves the title, original text, author attribution, visit-counter graphic, hosting badge and a “Back Home” link.
- The page has a very small content surface and few interactions; its purpose is self-expression rather than a complex workflow.
- A link back to the original personal site is preserved, but it points to another archived route in the replay context.

### Assessment

- **Usefulness:** high as a primary-source artifact for studying personal-web culture; low as a current service.
- **Mobile usability:** readable at the inspected width.
- **Accessibility:** not fully assessed. The screenshot does not prove keyboard or screen-reader behavior.
- **Preservation:** the primary text and several page elements are available; completeness of all historical dependencies remains unverified.

## 3. Page: Welcome to How Computers Work

**Archive capture:** 2009-10-27 07:50:41 UTC  
**Original page:** `https://geocities.com/howcompworks/index.htm`  
**Archived replay:** `https://arquivo.pt/noFrame/replay/20091027075041/https://geocities.com/howcompworks/index.htm`

### Journey

Search `computers` → open the first result → inspect topic navigation → repeat at 390 px.

### Observed behavior

- Desktop view presents a large graphic title and two columns of topic links (e.g. microprocessor, hard disk, modem, mouse, monitor, digital camera, memory, printer).
- At 390 px, the graphic/title and right-side topics are clipped outside the viewport.
- The visible text extraction includes a community link and does not expose the graphical heading as structured text.
- A visible page route to a third-party community is preserved, but its current operational status was not verified.

### Assessment

- **Usefulness:** educational/archival, with a recognizable computer-literacy information structure.
- **Mobile usability:** weak at the inspected width due to horizontal clipping.
- **Information architecture:** the two-column category grouping is understandable on desktop.
- **Accessibility:** uncertain. The large visual heading and text extraction suggest that meaningful content may be embedded in graphics; inspect the original source and alternative text before making a conformance claim.

### Modernization opportunity

Preserve the topic taxonomy but replace the fixed graphic-and-column layout with responsive, semantic topic cards; make the heading real text; ensure all links have accessible names; retain the original capture as a source link.

## 4. Page: Dog's Gallery

**Archive capture:** 2009-04-27 17:29:00 UTC  
**Original page:** `https://geocities.com/angelacater/dogsgallery.html`  
**Archived replay:** `https://arquivo.pt/noFrame/replay/20090427172900/https://geocities.com/angelacater/dogsgallery.html`

### Journey

Search `dogs` → open the result for a dog portrait gallery → inspect image/text pairing at 390 px.

### Observed behavior

- The archive replay preserves the gallery introduction, artist-authored descriptions, multiple portrait images, contact/commissioning links and next/back navigation.
- The layout uses bordered two-column table rows to pair each image with descriptive text.
- At 390 px, the first row gives the image a large share of the viewport and compresses the accompanying description into a narrow column; subsequent rows also produce cramped text next to image thumbnails.
- Images remain visible in the inspected screenshot, so this is not simply a page with missing media.

### Assessment

- **Usefulness:** high as an archival portfolio and record of personal creative work.
- **Mobile usability:** weak-to-mixed because the fixed table layout constrains text width.
- **Preservation:** both descriptive text and several images are present in the replay.
- **Accessibility:** not fully assessed; image alternatives and keyboard flow require source-level inspection.

### Modernization opportunity

Use a responsive gallery where each artwork becomes a semantic figure with an image, caption and descriptive text. On narrow screens, stack image and description vertically; preserve the artist's words and attribution.

## 5. Cross-site findings

1. GeoCities pages are not one design system. They range from a single-column diary to fixed educational navigation to table-driven visual portfolios.
2. Simple text pages may remain readable on mobile without redesign, while fixed-width graphics/tables create predictable reflow problems.
3. An archive's search result, replay wrapper, no-frame replay, screenshot, extracted text and original-file download are distinct evidence sources. They should not be treated as interchangeable.
4. The archive date is the exact capture timestamp, not necessarily the page's publication date. Arquivo.pt's own help documentation makes this distinction explicit.
5. Missing assets or incomplete captures should be logged as preservation gaps, not automatically diagnosed as original-site defects.

## 6. Site: Textfiles.com / BBS archive

**Historical snapshots:** 1999-01-25 (home page), 2001-06-24 (BBS directory), 2001-03-04 (general computer index), and 2001-07-24 (representative text file).

**Representative captures:**
- [Textfiles home, 1999-01-25](https://web.archive.org/web/19990125103815/http://www.textfiles.com/)
- [BBS Textfiles directory, 2001-06-24](https://web.archive.org/web/20010624153533/http://www.textfiles.com/bbs/)
- [General Computer Textfiles, 2001-03-04](https://web.archive.org/web/20010304201536/http://www.textfiles.com/computers/)
- [The 12 Commandments of BBS Users, 2001-07-24](https://web.archive.org/web/20010724080517/http://www.textfiles.com/bbs/12budord.txt)

### Journey

Open the 1999 home snapshot → enter the BBS archive → browse the BBS index → open a representative plain-text artifact → repeat the directory view at 390 px.

### Observed behavior

- The 1999 home capture explains the archive's purpose: preserving text-based culture, especially mid-1980s files and related material from earlier decades.
- The BBS directory is a long, categorized index with filename, size and description columns. It explains the social and technical role of bulletin board systems, then offers directories and individual files.
- The general computer index exposes practical material such as diskette formats, Atari storage modifications, serial interfaces, modem information and hardware notes.
- At 390 px, the introductory prose wraps, but the three-column directory table becomes narrow and forces filenames/descriptions into constrained columns.
- A representative plain-text artifact remains readable in a monospaced layout. The end of the file contains repeated SUB control characters, which the replay renders as visible junk characters rather than hiding them cleanly.
- The live-origin scrape did not return usable content in this inspection. That is an inspection/access result, not proof that the origin site is offline.

### Assessment

- **Usefulness:** high as a technical and cultural archive; the file index remains a valuable discovery structure.
- **Mobile usability:** mixed. Prose is readable; fixed tabular metadata is difficult at narrow widths.
- **Preservation:** text files and directory descriptions are available in the archived captures; control characters and external dependencies can degrade replay fidelity.
- **Accessibility:** not formally tested. A semantic table may be navigable, but narrow layout and raw control characters remain barriers to verify.

### Modernization opportunity

Keep the collection taxonomy and original file identity, but add responsive file cards, searchable descriptions, file-size metadata, a plain-text reader that visibly reports removed control bytes, and stable links to the archived source. Never silently alter the original archival bytes.

## 7. Site: The Million Dollar Homepage

**Inspected URL:** `https://milliondollarhomepage.com/`  
**Inspection date:** 2026-11-03  
**Evidence:** direct parse of the served HTML response; 59,257 bytes.

### Observed source structure

- The page has one image map with **251 `<area>` hotspots**.
- All 251 inspected hotspots have an `href` and a `title`, but none has an `alt` attribute.
- 80 hotspot elements have the `wayback-replaced` class and preserve their previous destination in `data-original-url`.
- The document includes 3 image elements, 10 ordinary anchor elements, 4 script elements, one frame element and one form element.
- A comment in the served HTML calls this a “Modified Version”, states that broken links have been replaced with Wayback Machine snapshots, and claims 1,164 replacements generated on 2026-01-23. The direct parse verified 80 rewritten image-map hotspots on this homepage; it did **not** independently verify the 1,164 figure or its scope.

### Assessment

- **Usefulness:** historically important as a one-page pixel-advertising experiment and as a working example of an image-map-heavy site.
- **Information architecture:** the core canvas is visually compact, while each hotspot carries a title and destination.
- **Accessibility risk:** high-priority structural issue. The `<area>` elements lack `alt` text. Their `title` attributes may provide some assistive-technology exposure, but this was not validated with screen readers and is not equivalent evidence to a proper alternative text.
- **Preservation:** some dead targets have been routed to Wayback snapshots while the original destination is retained in page markup; 80 such area rewrites were directly counted in this sample.
- **Unknown:** keyboard behavior, screen-reader naming, mobile hotspot usability and success of each archived destination have not been tested.

### Modernization opportunity

Retain the pixel-canvas metaphor, but provide a parallel, searchable directory of the same destinations with meaningful link names, domain labels and explicit “live/original” versus “archived snapshot” state. Treat image-map `alt` generation as a human-reviewed content task; do not blindly copy promotional `title` strings into `alt` and call the page accessible.

## 8. Research limitations

- No human participants or assistive-technology users were involved.
- No formal keyboard-only or screen-reader walkthrough was completed.
- No automated contrast/semantic audit was run against every archived page.
- The replayed pages may use archive-specific URL rewriting; a missing or redirected link can be an archive limitation rather than an original-site defect.
- The live CLI API integration could not be run from the build container due to network/DNS restrictions; unit tests use controlled API responses. Actual API endpoints were separately tested during research.
