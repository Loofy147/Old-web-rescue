import test from 'node:test';
import assert from 'node:assert/strict';
import { parseImageMaps, normalizeDestination, summarizeRegions } from '../pixel-atlas-core.mjs';

const BASE = 'https://legacy.example.org/gallery/index.html';

function parse(markup, options = {}) {
  return parseImageMaps(markup, { baseUrl: BASE, ...options });
}

test('extracts image-map regions and resolves relative destinations without losing raw attributes', () => {
  const result = parse(`
    <img src="board.jpg" width="640" height="400" usemap="#atlas">
    <map id="atlas" name="atlas">
      <area shape="rect" coords="10,20,110,90" href="../shop/item?id=7#details" alt="Open item seven" title="Item seven">
    </map>
  `);

  assert.equal(result.regions.length, 1);
  assert.equal(result.regions[0].shape, 'rect');
  assert.deepEqual(result.regions[0].coords, [10, 20, 110, 90]);
  assert.equal(result.regions[0].coordsRaw, '10,20,110,90');
  assert.equal(result.regions[0].hrefRaw, '../shop/item?id=7#details');
  assert.equal(result.regions[0].hrefResolved, 'https://legacy.example.org/shop/item?id=7#details');
  assert.equal(result.regions[0].label, 'Open item seven');
  assert.equal(result.regions[0].labelSource, 'alt');
  assert.equal(result.regions[0].labelStatus, 'verified-source-label');
  assert.equal(result.images[0].src, 'board.jpg');
  assert.equal(result.images[0].width, 640);
  assert.equal(result.images[0].height, 400);
  assert.deepEqual(result.maps[0].imageRefs, ['board.jpg']);
});

test('treats title-only text as a review candidate, not as a verified alternative', () => {
  const result = parse('<map name="m"><area href="/x" coords="0,0,10,10" title="Promotional tile"></map>');
  const region = result.regions[0];
  assert.equal(region.label, 'Promotional tile');
  assert.equal(region.labelSource, 'title');
  assert.equal(region.labelStatus, 'needs-review');
  assert.ok(region.warnings.includes('missing-alt'));
});

test('keeps an unlabelled destination in the inventory and exposes a missing-label warning', () => {
  const result = parse('<map id="m"><area href="https://target.example/" coords="0,0,10,10"></map>');
  const region = result.regions[0];
  assert.equal(region.label, null);
  assert.equal(region.labelStatus, 'missing');
  assert.ok(region.warnings.includes('missing-label'));
  assert.equal(region.hrefResolved, 'https://target.example/');
});

test('does not silently turn an empty alt attribute into a content label', () => {
  const result = parse('<map><area href="/decorative" coords="0,0,10,10" alt="" title="Decorative hint"></map>');
  const region = result.regions[0];
  assert.equal(region.label, 'Decorative hint');
  assert.equal(region.labelSource, 'title');
  assert.equal(region.labelStatus, 'needs-review');
  assert.ok(region.warnings.includes('empty-alt'));
});

test('identifies duplicate normalized destinations across regions', () => {
  const result = parse(`
    <map name="m">
      <area href="/same" coords="0,0,10,10" alt="First">
      <area href="https://legacy.example.org/same" coords="10,0,20,10" alt="Second">
      <area href="/other" coords="20,0,30,10" alt="Third">
    </map>
  `);
  assert.equal(result.regions[0].duplicateDestinationCount, 2);
  assert.equal(result.regions[1].duplicateDestinationCount, 2);
  assert.equal(result.regions[2].duplicateDestinationCount, 1);
  assert.ok(result.regions[0].warnings.includes('duplicate-destination'));
  assert.ok(!result.regions[2].warnings.includes('duplicate-destination'));
});

test('distinguishes an archived replacement and preserves the original destination', () => {
  const result = parse(`
    <map name="m">
      <area class="wayback-replaced" href="https://web.archive.org/web/20200102030405id_/https://old.example.org/catalog/item" data-original-url="https://old.example.org/catalog/item" coords="0,0,20,20" title="Catalog item">
    </map>
  `);
  const region = result.regions[0];
  assert.equal(region.destinationStatus, 'archive-replacement');
  assert.equal(region.archiveUrl, 'https://web.archive.org/web/20200102030405id_/https://old.example.org/catalog/item');
  assert.equal(region.originalUrl, 'https://old.example.org/catalog/item');
  assert.equal(region.hrefResolved, region.archiveUrl);
});

test('recovers the original URL from a Wayback target when no data-original-url exists', () => {
  const result = parse('<map><area href="https://web.archive.org/web/20221201000000/https://old.example.org/a%20b?x=1" coords="0,0,10,10" alt="Old page"></map>');
  const region = result.regions[0];
  assert.equal(region.destinationStatus, 'archive-replacement');
  assert.equal(region.originalUrl, 'https://old.example.org/a%20b?x=1');
  assert.equal(region.archiveUrl, 'https://web.archive.org/web/20221201000000/https://old.example.org/a%20b?x=1');
});

test('normalizes relative, root-relative and absolute URLs while preserving query and fragment', () => {
  assert.equal(normalizeDestination('../docs/page.html?mode=full#top', BASE), 'https://legacy.example.org/docs/page.html?mode=full#top');
  assert.equal(normalizeDestination('/docs/page.html', BASE), 'https://legacy.example.org/docs/page.html');
  assert.equal(normalizeDestination('https://external.example/a?x=1#y', BASE), 'https://external.example/a?x=1#y');
  assert.equal(normalizeDestination('javascript:alert(1)', BASE), null);
  assert.equal(normalizeDestination('mailto:archive@example.org', BASE), null);
});

test('flags malformed geometry but retains the region for review', () => {
  const result = parse(`
    <map name="m">
      <area shape="rect" coords="1,2,3" href="/bad" alt="Broken rectangle">
      <area shape="poly" coords="1,2,3,4,5" href="/odd" alt="Broken polygon">
      <area shape="circle" coords="a,2,3" href="/nan" alt="Invalid circle">
    </map>
  `);
  assert.equal(result.regions.length, 3);
  assert.equal(result.regions[0].geometryStatus, 'invalid');
  assert.ok(result.regions[0].warnings.includes('invalid-coordinate-count'));
  assert.ok(result.regions[1].warnings.includes('invalid-coordinate-count'));
  assert.ok(result.regions[2].warnings.includes('non-numeric-coordinate'));
});

test('records malformed or incomplete area elements instead of crashing', () => {
  const result = parse('<map id="broken"><area alt="No destination" shape="rect" coords="0,0,10"><area href="/ok" alt="Valid" shape="default"></map>');
  assert.equal(result.regions.length, 2);
  assert.ok(result.regions[0].warnings.includes('missing-href'));
  assert.ok(result.regions[0].warnings.includes('invalid-coordinate-count'));
  assert.equal(result.regions[1].geometryStatus, 'valid');
});

test('matches map names and ids to image usemap references', () => {
  const result = parse(`
    <img src="one.png" usemap="#first" width="300" height="100">
    <img src="two.png" usemap="#second">
    <map id="first"><area href="/one" alt="One" shape="default"></map>
    <map name="second"><area href="/two" alt="Two" shape="default"></map>
  `);
  assert.deepEqual(result.maps[0].imageRefs, ['one.png']);
  assert.deepEqual(result.maps[1].imageRefs, ['two.png']);
  assert.equal(result.regions[0].mapId, 'first');
  assert.equal(result.regions[1].mapId, 'second');
});

test('handles an empty document and reports zero counts', () => {
  const result = parse('<html><body><p>No image maps here.</p></body></html>');
  assert.deepEqual(result.maps, []);
  assert.deepEqual(result.regions, []);
  assert.deepEqual(summarizeRegions(result.regions), {
    total: 0,
    verifiedLabels: 0,
    reviewLabels: 0,
    missingLabels: 0,
    archiveReplacements: 0,
    duplicateDestinations: 0,
    geometryWarnings: 0,
  });
});

test('handles commented-out and script-contained fake area markup as non-content', () => {
  const result = parse(`
    <!-- <map><area href="/comment" alt="Comment"></map> -->
    <script>const example = '<area href="/script" alt="Not a real element">';</script>
    <map name="real"><area href="/real" alt="Real"></map>
  `);
  assert.equal(result.regions.length, 1);
  assert.equal(result.regions[0].hrefResolved, 'https://legacy.example.org/real');
});

test('preserves unquoted trailing slashes and decodes common HTML entities', () => {
  const result = parse('<map name=m><area shape=default href=/archive/ alt="Maps &amp; memories"></map>');
  assert.equal(result.regions[0].hrefRaw, '/archive/');
  assert.equal(result.regions[0].hrefResolved, 'https://legacy.example.org/archive/');
  assert.equal(result.regions[0].label, 'Maps & memories');
});

test('retains orphan area elements as explicit unassociated inventory entries', () => {
  const result = parse('<area href="/orphan" alt="Outside map" shape="default">');
  assert.equal(result.regions.length, 1);
  assert.equal(result.regions[0].mapId, null);
  assert.ok(result.regions[0].warnings.includes('area-outside-map'));
  assert.equal(result.summary.total, 1);
  assert.equal(result.diagnostics[0].code, 'area-outside-map');
});

test('reports an invalid base URL instead of silently losing relative-link resolution', () => {
  const result = parseImageMaps('<map><area href="/relative" alt="Relative" shape="default"></map>', { baseUrl: 'javascript:alert(1)' });
  assert.equal(result.provenance.baseUrl, null);
  assert.equal(result.regions[0].hrefResolved, null);
  assert.ok(result.diagnostics.some((item) => item.code === 'invalid-base-url'));
});

test('ignores fake map markup inside textarea, title and legacy raw-text elements', () => {
  const result = parse(`
    <textarea><map><area href="/textarea" alt="Not a map"></map></textarea>
    <title><map><area href="/title" alt="Not a map"></map></title>
    <xmp><map><area href="/xmp" alt="Not a map"></map></xmp>
    <map id="real"><area href="/real" alt="Real region" shape="default"></map>
  `);
  assert.equal(result.regions.length, 1);
  assert.equal(result.regions[0].hrefResolved, 'https://legacy.example.org/real');
});

test('parses the checked-in synthetic fixture and retains all eight regions', async () => {
  const { readFile } = await import('node:fs/promises');
  const { fileURLToPath } = await import('node:url');
  const path = new URL('../fixtures/demo-image-map.html', import.meta.url);
  const fixture = await readFile(fileURLToPath(path), 'utf8');
  const result = parse(fixture, { baseUrl: 'https://old.example.org/gallery/reading-room.html' });
  assert.equal(result.regions.length, 8);
  assert.equal(result.summary.archiveReplacements, 1);
  assert.equal(result.summary.verifiedLabels, 4);
  assert.equal(result.summary.reviewLabels, 3);
  assert.equal(result.summary.missingLabels, 1);
  assert.equal(result.summary.geometryWarnings, 1);
  assert.ok(result.regions.some((region) => region.warnings.includes('invalid-or-unsafe-href')));
});
