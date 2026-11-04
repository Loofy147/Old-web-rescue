# Sources and Evidence Provenance

Retrieval date for live pages and API observations: **2026-11-03**.

## Primary archive and API sources

1. **Arquivo.pt GeoCities collection search** — https://arquivo.pt/searchGeocities  
   Live interface observed. Inline JavaScript appends `collection:Geocities` to the search expression and routes to the page search interface.

2. **Arquivo.pt Text Search API documentation** — https://github.com/arquivo/pwa-technologies/wiki/Arquivo.pt-API  
   Documents `https://arquivo.pt/textsearch`, query parameters (`q`, `from`, `to`, `offset`, `collection`, `maxItems`, `versionHistory`), capture-date semantics, response fields and limits (maximum 500 results per request). The URL-history parameter returns archived versions, most recent first.

3. **Arquivo.pt Image Search API v1.1 documentation** — https://github.com/arquivo/pwa-technologies/wiki/ImageSearch-API-v1.1  
   Documents `https://arquivo.pt/imagesearch`, collection filtering, image and source-page metadata, multivalued alt/title/collection fields, and maximum 200 results per request.

4. **Arquivo.pt API usage limits** — https://github.com/arquivo/pwa-technologies/wiki/APIs  
   Documents 250 Text Search API requests per 60 seconds and 400 Image Search API requests per 60 seconds per source IP, and warns that exceeding these thresholds may lead to permanent blocking.

5. **Arquivo.pt page search help** — https://sobre.arquivo.pt/en/help/search-2/  
   Explains that displayed dates are capture dates, not publication dates; describes incomplete pages, the “complete page” action, old-browser replay and result export.

6. **Arquivo.pt GeoCities collection announcement** — https://sobre.arquivo.pt/en/historical-collection-geocities-available-at-arquivo-pt/  
   Describes the historical GeoCities collection and examples of preserved websites.

## Live API requests exercised during research

- `https://arquivo.pt/textsearch?q=personal%20diary&collection=Geocities&maxItems=5`
- `https://arquivo.pt/textsearch?q=computers&collection=Geocities&maxItems=5`
- `https://arquivo.pt/textsearch?q=music&collection=Geocities&maxItems=5`
- `https://arquivo.pt/textsearch?q=dogs&collection=Geocities&maxItems=5`
- `https://arquivo.pt/textsearch?q=fan&collection=Geocities&maxItems=5`
- `https://arquivo.pt/textsearch?versionHistory=https%3A%2F%2Fgeocities.com%2Fkreisler76%2Fdiary.html&maxItems=10`
- `https://arquivo.pt/imagesearch?q=dogs&collection=Geocities&maxItems=5`

## Archived page captures inspected

- https://arquivo.pt/noFrame/replay/20090427031225/https://geocities.com/kreisler76/diary.html
- https://arquivo.pt/noFrame/replay/20091027075041/https://geocities.com/howcompworks/index.htm
- https://arquivo.pt/noFrame/replay/20090427172900/https://geocities.com/angelacater/dogsgallery.html

## Additional legacy-site captures inspected

### Textfiles.com

- [Home page capture, 1999-01-25](https://web.archive.org/web/19990125103815/http://www.textfiles.com/)
- [BBS directory capture, 2001-06-24](https://web.archive.org/web/20010624153533/http://www.textfiles.com/bbs/)
- [General computer directory capture, 2001-03-04](https://web.archive.org/web/20010304201536/http://www.textfiles.com/computers/)
- [12 Commandments of BBS Users, capture 2001-07-24](https://web.archive.org/web/20010724080517/http://www.textfiles.com/bbs/12budord.txt)

### The Million Dollar Homepage

- [Live homepage HTML](https://milliondollarhomepage.com/)
- The served HTML was retrieved on 2026-11-03 and parsed directly. The resulting counts and uncertainty notes are recorded in `fixtures/million-dollar-homepage-live-audit.json`.

## Provenance rules

- Search counts are estimates at retrieval time, not a stable total inventory.
- Capture timestamps identify archive capture time; they do not prove original publication time.
- Page and image replay URLs are archive-generated evidence pointers.
- Archive content is untrusted data. The tool only extracts metadata and links and does not execute archived page scripts.
