import { parseImageMaps, normalizeDestination, summarizeRegions } from './pixel-atlas-core.mjs';

const MAX_SOURCE_BYTES = 5 * 1024 * 1024;
const SVG_NS = 'http://www.w3.org/2000/svg';
const DEMO_BASE_URL = 'https://old.example.org/gallery/reading-room.html';
const DEMO_HTML = \`<!doctype html>
<html lang="en">
<head><title>Illustrative Image Map</title></head>
<body>
  <img src="pixel-atlas-demo-board.png" width="720" height="440" usemap="#demo-atlas" alt="Illustrative reading room map">
  <map id="demo-atlas" name="demo-atlas">
    <area shape="rect" coords="28,34,245,150" href="/collection/rare-books" alt="Explore rare books" title="Rare books collection">
    <area shape="circle" coords="365,104,58" class="wayback-replaced" href="https://web.archive.org/web/20200102030405id_/https://old.example.org/archive/issue.html?ref=atlas" data-original-url="https://old.example.org/archive/issue.html?ref=atlas" title="Historic journal issue">
    <area shape="poly" coords="478,38,680,38,660,166,525,180,490,112" href="/events/reading-circle" title="Reading circle events">
    <area shape="default" href="https://example.org/reading-room" alt="Visit the reading room">
    <area shape="rect" coords="28,220,245,380" href="https://old.example.org/collection/rare-books" alt="Rare books collection duplicate">
    <area shape="circle" coords="x,290,58" href="/issues/archived-number" title="A historic issue with malformed geometry">
    <area shape="rect" coords="485,235,680,385" href="javascript:alert(1)" alt="Unsafe script destination">
    <area shape="rect" coords="250,390,310,420">
  </map>
</body>
</html>\`;

const byId = (id) => document.getElementById(id);
const elements = {
  sourceHtml: byId('source-html'),
  sourceFile: byId('source-file'),
  fileName: byId('file-name'),
  baseUrl: byId('base-url'),
  analyze: byId('analyze-button'),
  loadSample: byId('load-sample'),
  importStatus: byId('import-status'),
  results: byId('results'),
  emptyState: byId('empty-state'),
  resultsSubtitle: byId('results-subtitle'),
  metricTotal: byId('metric-total'),
  metricVerified: byId('metric-verified'),
  metricReview: byId('metric-review'),
  metricArchive: byId('metric-archive'),
  mapDimension: byId('map-dimension'),
  geometryBoard: byId('geometry-board'),
  geometryNote: byId('geometry-note'),
  search: byId('region-search'),
  regionCount: byId('region-count'),
  filterStatus: byId('filter-status'),
  regionList: byId('region-list'),
  emptyResults: byId('empty-results'),
  provenance: byId('provenance-details'),
  exportCsv: byId('export-csv'),
  exportJson: byId('export-json'),
};

let analysis = null;
let sourceName = 'Pasted HTML';
let sourceMode = 'pasted';
let selectedRegionIndex = null;
let lastFilteredRegions = [];

function setStatus(message, kind = 'normal') {
  elements.importStatus.textContent = message;
  elements.importStatus.className = \`status-line\${kind === 'normal' ? '' : \` \${kind}\`}\`;
}

function makeElement(tag, className, text = null) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== null) node.textContent = String(text);
  return node;
}

function safeExternalLink(rawUrl, label) {
  const safeUrl = normalizeDestination(rawUrl);
  if (!safeUrl) return null;
  const link = makeElement('a', '', label);
  link.href = safeUrl;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  link.referrerPolicy = 'no-referrer';
  return link;
}

function formatShape(shape) {
  const names = { rect: 'Rectangle', circle: 'Circle', poly: 'Polygon', polygon: 'Polygon', default: 'Default area' };
  return names[shape] || \`Unknown: \${shape}\`;
}

function warningLabel(code, region) {
  const labels = {
    'missing-alt': 'ALT NOT PROVIDED',
    'empty-alt': 'ALT IS EMPTY',
    'missing-label': 'LABEL NEEDED',
    'duplicate-destination': \`DUPLICATE TARGET × \${region.duplicateDestinationCount}\`,
    'invalid-coordinate-count': 'COORDINATE COUNT INVALID',
    'non-numeric-coordinate': 'COORDINATE NOT NUMERIC',
    'missing-coordinates': 'COORDINATES MISSING',
    'unknown-shape': 'UNKNOWN SHAPE',
    'missing-href': 'DESTINATION MISSING',
    'invalid-or-unsafe-href': 'UNSAFE OR INVALID DESTINATION',
    'invalid-original-url': 'ORIGINAL URL INVALID',
    'original-url-unavailable': 'ORIGINAL URL UNAVAILABLE',
    'area-outside-map': 'AREA OUTSIDE MAP',
  };
  return labels[code] || code.toUpperCase().replaceAll('-', ' ');
}

function renderSummary() {
  const summary = analysis.summary;
  elements.metricTotal.textContent = String(summary.total);
  elements.metricVerified.textContent = String(summary.verifiedLabels);
  elements.metricReview.textContent = String(summary.reviewLabels + summary.missingLabels);
  elements.metricArchive.textContent = String(summary.archiveReplacements);
  elements.regionCount.textContent = String(summary.total);
}

function renderGeometry() {
  const board = elements.geometryBoard;
  board.replaceChildren();
  const regions = analysis.regions;
  const mappedImage = analysis.images.find((image) => image.mapId) || analysis.images[0] || null;

  if (regions.length === 0) {
    board.append(makeBoardEmpty('No image-map regions found', 'The source may contain no <area> elements inside a <map>.'));
    elements.mapDimension.textContent = 'NO REGIONS';
    elements.geometryNote.textContent = 'No image-map areas were available to plot.';
    return;
  }

  const numericPoints = regions
    .filter((region) => region.geometryStatus === 'valid' && region.coords.length)
    .flatMap((region) => region.coords);
  const derivedWidth = Math.max(1, ...numericPoints.filter((_, index) => index % 2 === 0));
  const derivedHeight = Math.max(1, ...numericPoints.filter((_, index) => index % 2 === 1));
  const width = mappedImage?.width || Math.max(derivedWidth, 640);
  const height = mappedImage?.height || Math.max(derivedHeight, 360);

  const svg = document.createElementNS(SVG_NS, 'svg');
  svg.classList.add('geometry-svg');
  svg.setAttribute('viewBox', \`0 0 \${width} \${height}\`);
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  svg.setAttribute('aria-hidden', 'true');
  svg.setAttribute('focusable', 'false');

  let drawn = 0;
  let skipped = 0;
  for (const region of regions) {
    if (region.geometryStatus !== 'valid') {
      skipped += 1;
      continue;
    }
    const coords = region.coords;
    const shape = document.createElementNS(SVG_NS, region.shape === 'poly' || region.shape === 'polygon' ? 'polygon' : 'rect');
    if (region.shape === 'rect' && coords.length === 4) {
      const [x1, y1, x2, y2] = coords;
      shape.setAttribute('x', String(Math.min(x1, x2)));
      shape.setAttribute('y', String(Math.min(y1, y2)));
      shape.setAttribute('width', String(Math.max(1, Math.abs(x2 - x1))));
      shape.setAttribute('height', String(Math.max(1, Math.abs(y2 - y1))));
    } else if (region.shape === 'circle' && coords.length === 3) {
      const [cx, cy, radius] = coords;
      const circle = document.createElementNS(SVG_NS, 'circle');
      circle.setAttribute('cx', String(cx));
      circle.setAttribute('cy', String(cy));
      circle.setAttribute('r', String(Math.max(1, radius)));
      circle.classList.add('geometry-region');
      if (region.index === selectedRegionIndex) circle.classList.add('is-selected');
      if (region.warnings.length) circle.classList.add('has-issue');
      const title = document.createElementNS(SVG_NS, 'title');
      title.textContent = \`Region \${region.index}\`;
      circle.append(title);
      svg.append(circle);
      drawn += 1;
      continue;
    } else if (region.shape === 'poly' || region.shape === 'polygon') {
      const pairs = [];
      for (let index = 0; index < coords.length; index += 2) pairs.push(\`\${coords[index]},\${coords[index + 1]}\`);
      shape.setAttribute('points', pairs.join(' '));
    } else if (region.shape === 'default') {
      // Default areas cover the entire source image; render a boundary because
      // multiple default regions cannot be spatially distinguished.
      const defaultRect = document.createElementNS(SVG_NS, 'rect');
      defaultRect.setAttribute('x', '1');
      defaultRect.setAttribute('y', '1');
      defaultRect.setAttribute('width', String(Math.max(1, width - 2)));
      defaultRect.setAttribute('height', String(Math.max(1, height - 2)));
      defaultRect.classList.add('geometry-region');
      if (region.index === selectedRegionIndex) defaultRect.classList.add('is-selected');
      const title = document.createElementNS(SVG_NS, 'title');
      title.textContent = \`Region \${region.index}: default area\`;
      defaultRect.append(title);
      svg.append(defaultRect);
      drawn += 1;
      continue;
    } else {
      skipped += 1;
      continue;
    }

    shape.classList.add('geometry-region');
    if (region.index === selectedRegionIndex) shape.classList.add('is-selected');
    if (region.warnings.length) shape.classList.add('has-issue');
    const title = document.createElementNS(SVG_NS, 'title');
    title.textContent = \`Region \${region.index}\`;
    shape.append(title);
    svg.append(shape);

    const label = document.createElementNS(SVG_NS, 'text');
    label.classList.add('geometry-label');
    label.textContent = String(region.index);
    if (region.shape === 'rect' && coords.length === 4) {
      label.setAttribute('x', String((coords[0] + coords[2]) / 2));
      label.setAttribute('y', String((coords[1] + coords[3]) / 2));
    } else if ((region.shape === 'poly' || region.shape === 'polygon') && coords.length >= 6) {
      label.setAttribute('x', String(coords.filter((_, index) => index % 2 === 0).reduce((a, b) => a + b, 0) / (coords.length / 2)));
      label.setAttribute('y', String(coords.filter((_, index) => index % 2 === 1).reduce((a, b) => a + b, 0) / (coords.length / 2)));
    }
    if (label.hasAttribute('x')) svg.append(label);
    drawn += 1;
  }

  if (drawn === 0) {
    board.append(makeBoardEmpty('No plottable regions', 'All regions have missing or invalid geometry. They remain available in the searchable inventory.'));
  } else {
    board.append(svg);
  }
  elements.mapDimension.textContent = \`\${Math.round(width)} × \${Math.round(height)} PX\`;
  elements.geometryNote.textContent = \`\${drawn} region\${drawn === 1 ? '' : 's'} plotted\${skipped ? \` · \${skipped} geometry issue\${skipped === 1 ? '' : 's'} omitted\` : ''}. Coordinate view is schematic; no source image is fetched.\`;
}

function makeBoardEmpty(heading, description) {
  const wrapper = makeElement('div', 'board-empty');
  wrapper.append(makeElement('span', '', '⌗'), makeElement('strong', '', heading), makeElement('p', '', description));
  return wrapper;
}

function createBadge(text, kind = '') {
  return makeElement('span', \`region-status\${kind ? \` \${kind}\` : ''}\`, text);
}

function renderRegionCard(region) {
  const card = makeElement('article', 'region-card');
  if (region.index === selectedRegionIndex) card.classList.add('selected');
  const top = makeElement('div', 'region-top');
  const select = makeElement('button', 'region-select');
  select.type = 'button';
  select.setAttribute('aria-pressed', String(region.index === selectedRegionIndex));
  select.setAttribute('aria-label', \`Locate region \${region.index}: \${region.label || 'source label missing'}\`);
  const number = makeElement('span', 'region-number', String(region.index).padStart(2, '0'));
  const titleWrap = makeElement('span', 'region-title-wrap');
  const title = region.label || \`Region \${region.index} — no source label\`;
  titleWrap.append(makeElement('span', 'region-title', title));
  const meta = makeElement('span', 'region-meta', \`\${formatShape(region.shape)} · \${region.mapId ? \`Map \${region.mapId}\` : 'Unassociated area'}\`);
  titleWrap.append(meta);
  select.append(number, titleWrap);
  select.addEventListener('click', () => {
    selectedRegionIndex = region.index;
    renderGeometry();
    renderRegionList();
  });

  const labelBadge = region.labelStatus === 'verified-source-label'
    ? createBadge('SOURCE LABEL', 'good')
    : region.labelStatus === 'needs-review'
      ? createBadge('TITLE ONLY', 'review')
      : createBadge('MISSING LABEL', 'missing');
  top.append(select, labelBadge);
  card.append(top);

  if (region.warnings.length) {
    const warningRow = makeElement('div', 'region-warnings');
    for (const warning of region.warnings) {
      const kind = warning === 'missing-label' || warning === 'invalid-or-unsafe-href' || warning === 'non-numeric-coordinate'
        ? ' issue'
        : '';
      warningRow.append(makeElement('span', \`warning-chip\${kind}\`, warningLabel(warning, region)));
    }
    card.append(warningRow);
  }

  const links = makeElement('div', 'destination-row');
  if (region.destinationStatus === 'archive-replacement') {
    links.append(makeElement('span', 'destination-kind', 'ARCHIVE REPLACEMENT'));
    const archived = safeExternalLink(region.archiveUrl, 'Open archived target ↗');
    if (archived) links.append(archived);
    const original = safeExternalLink(region.originalUrl, 'Original target ↗');
    if (original) links.append(original);
  } else if (region.destinationStatus === 'rewritten') {
    links.append(makeElement('span', 'destination-kind', 'REWRITTEN TARGET'));
    const displayed = safeExternalLink(region.hrefResolved, 'Open displayed target ↗');
    if (displayed) links.append(displayed);
    const original = safeExternalLink(region.originalUrl, 'Original target ↗');
    if (original) links.append(original);
  } else {
    links.append(makeElement('span', 'destination-kind', 'ORIGINAL TARGET'));
    const destination = safeExternalLink(region.hrefResolved, 'Open destination ↗');
    if (destination) links.append(destination);
    else links.append(makeElement('span', 'destination-kind', 'No safe HTTP(S) destination'));
  }
  if (links.childElementCount) card.append(links);

  const rawTarget = region.hrefRaw || '(no href attribute)';
  const rawLine = makeElement('p', 'destination-url');
  rawLine.append(makeElement('strong', '', 'Source href: '), document.createTextNode(rawTarget));
  card.append(rawLine);
  return card;
}

function renderRegionList() {
  const query = elements.search.value.trim().toLowerCase().replace(/[\\s_-]+/g, ' ');
  const all = analysis.regions;
  const filtered = all.filter((region) => {
    if (!query) return true;
    const searchable = [
      region.index, region.mapId, region.mapName, region.shape, region.coordsRaw,
      region.label, region.labelSource, region.labelStatus, region.title, region.alt,
      region.hrefRaw, region.hrefResolved, region.originalUrl, region.archiveUrl,
      region.destinationStatus, region.warnings.join(' '),
    ].filter(Boolean).join(' ').toLowerCase().replace(/[\\s_-]+/g, ' ');
    return searchable.includes(query);
  });
  lastFilteredRegions = filtered;
  elements.regionList.replaceChildren();
  for (const region of filtered) elements.regionList.append(renderRegionCard(region));
  elements.regionCount.textContent = \`\${filtered.length}/\${all.length}\`;
  elements.filterStatus.textContent = query
    ? \`\${filtered.length} of \${all.length} regions match “\${query}”.\`
    : \`\${all.length} region\${all.length === 1 ? '' : 's'} from \${analysis.maps.length} map\${analysis.maps.length === 1 ? '' : 's'}.\`;
  elements.emptyResults.hidden = filtered.length > 0;
  if (query && filtered.length === 0) elements.emptyResults.hidden = false;
}

function renderProvenance() {
  elements.provenance.replaceChildren();
  const summary = analysis.summary;
  const sourceUrl = analysis.provenance.baseUrl || 'Not supplied — absolute URLs only';
  const mapNames = analysis.maps.map((map) => map.name || map.id).join(', ') || 'No named maps';
  const diagnosticText = analysis.diagnostics.length
    ? analysis.diagnostics.map((item) => item.message).join(' ')
    : 'No parser-level structural diagnostics.';
  const items = [
    ['Source reference', \`\${sourceName} · \${sourceUrl}\`],
    ['Maps and images', \`\${analysis.maps.length} map(s): \${mapNames}. \${analysis.images.length} image element(s) detected.\`],
    ['Label quality', \`\${summary.verifiedLabels} source labels · \${summary.reviewLabels} title-only candidates · \${summary.missingLabels} missing labels.\`],
    ['Destination state', \`\${summary.archiveReplacements} archive replacement(s) · \${summary.duplicateDestinations} region(s) with duplicate destinations.\`],
    ['Geometry', \`\${summary.geometryWarnings} region(s) with invalid geometry. \${diagnosticText}\`],
    ['Execution boundary', 'HTML was parsed as text. Scripts, styles and embedded content were not executed. No network requests were made.'],
  ];
  for (const [heading, value] of items) {
    const item = makeElement('article', 'provenance-item');
    item.append(makeElement('strong', '', heading), makeElement('p', heading === 'Geometry' && analysis.diagnostics.length ? 'provenance-warning' : '', value));
    elements.provenance.append(item);
  }
}

function analyzeSource() {
  const source = elements.sourceHtml.value;
  const byteLength = new TextEncoder().encode(source).byteLength;
  if (!source.trim()) {
    setStatus('Paste HTML or choose a local file before analyzing.', 'error');
    elements.sourceHtml.focus();
    return;
  }
  if (byteLength > MAX_SOURCE_BYTES) {
    setStatus('Source exceeds the 5 MB inspection limit. Use a smaller saved page or extract the image-map section.', 'error');
    return;
  }

  const suppliedBase = elements.baseUrl.value.trim();
  if (suppliedBase && !normalizeDestination(suppliedBase)) {
    setStatus('The page URL must be an absolute HTTP(S) address. Correct it or leave it blank before analyzing.', 'error');
    elements.baseUrl.focus();
    return;
  }

  try {
    analysis = parseImageMaps(source, { baseUrl: suppliedBase || null });
    selectedRegionIndex = analysis.regions[0]?.index ?? null;
    elements.search.value = '';
    elements.results.hidden = false;
    elements.emptyState.hidden = true;
    elements.exportCsv.disabled = analysis.regions.length === 0;
    elements.exportJson.disabled = false;
    const mapLabel = \`\${analysis.maps.length} map\${analysis.maps.length === 1 ? '' : 's'}\`;
    elements.resultsSubtitle.textContent = \`\${analysis.regions.length} region\${analysis.regions.length === 1 ? '' : 's'} extracted from \${mapLabel}. Original attributes and destination provenance retained.\`;
    renderSummary();
    renderGeometry();
    renderRegionList();
    renderProvenance();

    if (analysis.regions.length) {
      const missing = analysis.summary.missingLabels;
      setStatus(\`Inspection complete: \${analysis.regions.length} region(s), \${missing} without a usable source label. Review the warnings before reusing these destinations.\`, 'success');
    } else {
      setStatus('No image-map regions were found. The HTML was parsed safely, but no <area> elements were available inside <map> blocks.', 'error');
    }
  } catch (error) {
    analysis = null;
    setStatus(\`Could not parse this source: \${error instanceof Error ? error.message : String(error)}\`, 'error');
  }
}

function downloadText(filename, content, contentType) {
  const blob = new Blob([content], { type: contentType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.hidden = true;
  document.body.append(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function csvCell(value) {
  const text = Array.isArray(value) ? value.join('|') : String(value ?? '');
  return \`"\${text.replaceAll('"', '""')}"\`;
}

function exportCsv() {
  if (!analysis) return;
  const columns = [
    ['index', 'region_index'], ['mapId', 'map_id'], ['shape', 'shape'], ['coordsRaw', 'coords'],
    ['label', 'label'], ['labelSource', 'label_source'], ['labelStatus', 'label_status'],
    ['destinationStatus', 'destination_status'], ['hrefRaw', 'href_raw'], ['hrefResolved', 'href_resolved'],
    ['originalUrl', 'original_url'], ['archiveUrl', 'archive_url'],
    ['duplicateDestinationCount', 'duplicate_destination_count'], ['warnings', 'warnings'],
  ];
  const rows = [columns.map(([, header]) => csvCell(header)).join(',')];
  for (const region of lastFilteredRegions) rows.push(columns.map(([key]) => csvCell(region[key])).join(','));
  downloadText('pixel-atlas-regions.csv', \`\\ufeff\${rows.join('\\r\\n')}\`, 'text/csv;charset=utf-8');
  setStatus(\`Exported \${lastFilteredRegions.length} currently visible region(s) to CSV.\`, 'success');
}

function exportJson() {
  if (!analysis) return;
  const payload = {
    product: 'Old Web Rescue Lab — Pixel Atlas',
    schemaVersion: '0.1',
    exportedAt: new Date().toISOString(),
    sourceName,
    ...analysis,
  };
  downloadText('pixel-atlas-analysis.json', JSON.stringify(payload, null, 2), 'application/json;charset=utf-8');
  setStatus('Exported the complete inspection and provenance record to JSON.', 'success');
}

function loadSample() {
  elements.sourceHtml.value = DEMO_HTML;
  elements.baseUrl.value = DEMO_BASE_URL;
  sourceName = 'Synthetic demonstration fixture';
  sourceMode = 'demo';
  elements.fileName.textContent = 'Synthetic demonstration fixture';
  setStatus('Synthetic example loaded. It contains original, archived, duplicate, missing-label and invalid-destination cases. Analyze it to inspect the records.');
  elements.sourceHtml.focus();
}

async function loadLocalFile(file) {
  if (!file) return;
  if (file.size > MAX_SOURCE_BYTES) {
    setStatus('File exceeds the 5 MB inspection limit.', 'error');
    elements.sourceFile.value = '';
    return;
  }
  try {
    const text = await file.text();
    elements.sourceHtml.value = text;
    sourceName = file.name;
    sourceMode = 'file';
    elements.fileName.textContent = file.name;
    setStatus(\`Loaded \${file.name} locally (\${file.size.toLocaleString()} bytes). No upload occurred.\`, 'success');
  } catch (error) {
    setStatus(\`Could not read the local file: \${error instanceof Error ? error.message : String(error)}\`, 'error');
  }
}

elements.loadSample.addEventListener('click', loadSample);
elements.analyze.addEventListener('click', analyzeSource);
elements.sourceFile.addEventListener('change', (event) => loadLocalFile(event.target.files?.[0]));
elements.search.addEventListener('input', () => {
  if (!analysis) return;
  renderRegionList();
});
elements.exportCsv.addEventListener('click', exportCsv);
elements.exportJson.addEventListener('click', exportJson);
elements.sourceHtml.addEventListener('input', () => {
  if (sourceMode !== 'file') {
    sourceMode = 'pasted';
    sourceName = 'Pasted/edited HTML';
    elements.fileName.textContent = 'Edited source';
  }
});
elements.sourceHtml.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') analyzeSource();
});

document.addEventListener('keydown', (event) => {
  const target = event.target;
  const isTyping = target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target?.isContentEditable;
  if (event.key === '/' && !isTyping && !event.ctrlKey && !event.metaKey && !event.altKey && analysis) {
    event.preventDefault();
    elements.search.focus();
  }
  if (event.key === 'Escape' && target === elements.search && elements.search.value) {
    elements.search.value = '';
    renderRegionList();
  }
});

// The example is synthetic and contains no archived third-party content.
