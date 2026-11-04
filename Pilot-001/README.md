# Old Web Rescue Lab — Pilot 001

A task-based investigation of long-lived and historically significant websites, plus an independent modernization prototype for one verified legacy failure.

## Deliverables

- `EVIDENCE.md` — findings, evidence URLs, limitations and rescue priorities.
- `audit.json` — machine-readable records for the inspected sites.
- `index.html`, `styles.css`, `app.mjs` — the accessible memory-game prototype.
- `memory-reboot.html` — self-contained one-file version for easy local opening.
- `build-standalone.mjs` — deterministic builder for the one-file version.
- `game-engine.mjs` — deterministic, framework-free game logic.
- `game-engine.test.mjs` — Node's built-in test suite.
- `browser-smoke.py` — optional Playwright browser check.

## Run the prototype

For the easiest route, open `memory-reboot.html` directly in a modern browser. It is self-contained and makes no background network requests.

The multi-file version is a static site with no server, database, analytics, accounts, network calls or third-party assets. Because JavaScript modules may be restricted when opening an HTML file directly, serve the folder locally:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000` in a modern browser.

## Run tests

The game logic uses only Node.js built-ins:

```bash
node --test game-engine.test.mjs
```

Optional browser verification requires Python Playwright and a Chromium browser:

```bash
python browser-smoke.py
```

The browser smoke script embeds the local files into an isolated browser document and verifies both the multi-file and standalone builds, so it does not need to contact an external service.

## Scope and intellectual-property boundary

The prototype rebuilds only the generic memory-game interaction pattern: reveal two cards, retain matches, conceal mismatches. It does not use Space Jam characters, imagery, music, source code or branding. It is independent and is not affiliated with Warner Bros.

## Research method

Every site is evaluated through one or more explicit user journeys rather than its homepage alone. Evidence types are separated:

- `ESTABLISHED`: directly observable in the inspected page, markup, archive capture or validator report.
- `EXPERIMENTALLY_SUPPORTED`: reproduced through a task or browser interaction in this run.
- `INFERENCE`: interpretation based on collected evidence.
- `UNKNOWN`: not tested or not reliably observable.

A Nu HTML Checker result is evidence about HTML conformance, not proof of accessibility, security, performance or overall quality. Screen-reader testing and human WCAG evaluation remain separate work.
