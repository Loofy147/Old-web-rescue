const SAFE_PROTOCOLS = new Set(['http:', 'https:']);
const WAYBACK_HOSTS = new Set(['web.archive.org', 'wayback.archive-it.org']);
const ARCHIVE_MODIFIERS = /^(?:id_|im_|if_|oe_|js_|cs_|mp_)+/i;
const RAW_TEXT_ELEMENTS = new Set(['script', 'style', 'textarea', 'title', 'xmp', 'iframe', 'noembed', 'noframes']);

function decodeEntities(value) {
  return String(value ?? '').replace(
    /&(#(?:x[0-9a-f]+|[0-9]+)|amp|quot|apos|lt|gt|nbsp);/gi,
    (match, entity) => {
      const key = entity.toLowerCase();
      if (key === 'amp') return '&';
      if (key === 'quot') return '"';
      if (key === 'apos') return "'";
      if (key === 'lt') return '<';
      if (key === 'gt') return '>';
      if (key === 'nbsp') return '\u00a0';
      if (key.startsWith('#x')) {
        const codePoint = Number.parseInt(key.slice(2), 16);
        return Number.isFinite(codePoint) && codePoint <= 0x10ffff ? String.fromCodePoint(codePoint) : match;
      }
      if (key.startsWith('#')) {
        const codePoint = Number.parseInt(key.slice(1), 10);
        return Number.isFinite(codePoint) && codePoint <= 0x10ffff ? String.fromCodePoint(codePoint) : match;
      }
      return match;
    },
  );
}

function findTagEnd(source, start) {
  let quote = null;
  for (let index = start; index < source.length; index += 1) {
    const char = source[index];
    if (quote) {
      if (char === quote) quote = null;
    } else if (char === '"' || char === "'") {
      quote = char;
    } else if (char === '>') {
      return index;
    }
  }
  return -1;
}

function parseAttributes(input) {
  const attributes = Object.create(null);
  let index = 0;
  while (index < input.length) {
    while (index < input.length && /\s|\//.test(input[index])) index += 1;
    if (index >= input.length) break;

    const nameStart = index;
    while (index < input.length && !/[\s=/>]/.test(input[index])) index += 1;
    if (index === nameStart) {
      index += 1;
      continue;
    }
    const name = input.slice(nameStart, index).toLowerCase();
    while (index < input.length && /\s/.test(input[index])) index += 1;

    let value = '';
    if (input[index] === '=') {
      index += 1;
      while (index < input.length && /\s/.test(input[index])) index += 1;
      const quote = input[index];
      if (quote === '"' || quote === "'") {
        index += 1;
        const valueStart = index;
        while (index < input.length && input[index] !== quote) index += 1;
        value = input.slice(valueStart, index);
        if (input[index] === quote) index += 1;
      } else {
        const valueStart = index;
        while (index < input.length && !/[\s>]/.test(input[index])) index += 1;
        value = input.slice(valueStart, index);
      }
    }
    if (!(name in attributes)) attributes[name] = decodeEntities(value);
  }
  return attributes;
}

function tokenizeTags(html) {
  const source = String(html ?? '');
  const tokens = [];
  const lowerSource = source.toLowerCase();
  let cursor = 0;

  while (cursor < source.length) {
    const opening = source.indexOf('<', cursor);
    if (opening < 0) break;

    if (source.startsWith('<!--', opening)) {
      const commentEnd = source.indexOf('-->', opening + 4);
      cursor = commentEnd < 0 ? source.length : commentEnd + 3;
      continue;
    }
    if (source.startsWith('<![CDATA[', opening)) {
      const cdataEnd = source.indexOf(']]>', opening + 9);
      cursor = cdataEnd < 0 ? source.length : cdataEnd + 3;
      continue;
    }

    const end = findTagEnd(source, opening + 1);
    if (end < 0) break;
    const inside = source.slice(opening + 1, end);
    cursor = end + 1;

    if (!inside || /^\s*[!?]/.test(inside)) continue;
    const closing = /^\s*\//.test(inside);
    const body = inside.replace(/^\s*\//, '').trimStart();
    const nameMatch = body.match(/^([a-zA-Z][\w:-]*)/);
    if (!nameMatch) continue;
    const name = nameMatch[1].toLowerCase();
    const attrText = body.slice(nameMatch[0].length);
    tokens.push({ name, closing, attrs: closing ? Object.create(null) : parseAttributes(attrText) });

    // Raw-text contents are not parsed as markup. This prevents fake <map>
    // strings inside scripts, styles, titles, textareas and legacy raw-text
    // elements from being imported as real image-map regions.
    if (!closing && name === 'plaintext') break;
    if (!closing && RAW_TEXT_ELEMENTS.has(name)) {
      const closeStart = lowerSource.indexOf(`</${name}`, cursor);
      if (closeStart < 0) break;
      const closeEnd = findTagEnd(source, closeStart + 2 + name.length);
      if (closeEnd < 0) break;
      tokens.push({ name, closing: true, attrs: Object.create(null) });
      cursor = closeEnd + 1;
    }
  }
  return tokens;
}

export function normalizeDestination(rawValue, baseUrl = null) {
  const raw = String(rawValue ?? '').trim();
  if (!raw) return null;
  try {
    const parsed = baseUrl ? new URL(raw, baseUrl) : new URL(raw);
    if (!SAFE_PROTOCOLS.has(parsed.protocol)) return null;
    parsed.username = '';
    parsed.password = '';
    return parsed.href;
  } catch {
    return null;
  }
}

function unwrapWaybackUrl(value) {
  if (!value) return null;
  try {
    const parsed = new URL(value);
    if (!WAYBACK_HOSTS.has(parsed.hostname.toLowerCase())) return null;
    const match = parsed.pathname.match(/^\/web\/[^/]+\/(.+)$/);
    if (!match) return null;
    let archivedTarget = `${match[1]}${parsed.search}${parsed.hash}`.replace(ARCHIVE_MODIFIERS, '');
    if (/^https?%3a/i.test(archivedTarget)) {
      try { archivedTarget = decodeURIComponent(archivedTarget); } catch { /* retain exact encoded value */ }
    }
    return normalizeDestination(archivedTarget);
  } catch {
    return null;
  }
}

function validateGeometry(shape, rawCoords) {
  const normalizedShape = String(shape || 'rect').trim().toLowerCase();
  const coordsText = String(rawCoords ?? '').trim();
  if (normalizedShape === 'default') {
    return { coords: [], status: 'valid', warnings: [] };
  }
  if (!coordsText) {
    return { coords: [], status: 'invalid', warnings: ['missing-coordinates', 'invalid-coordinate-count'] };
  }

  const parts = coordsText.split(/[\s,]+/).filter(Boolean);
  const coords = parts.map((part) => Number(part));
  if (coords.some((value) => !Number.isFinite(value) || !Number.isInteger(value) || value < 0)) {
    return { coords, status: 'invalid', warnings: ['non-numeric-coordinate'] };
  }

  let validCount = false;
  if (normalizedShape === 'rect') validCount = coords.length === 4;
  else if (normalizedShape === 'circle') validCount = coords.length === 3;
  else if (normalizedShape === 'poly' || normalizedShape === 'polygon') validCount = coords.length >= 6 && coords.length % 2 === 0;
  else return { coords, status: 'invalid', warnings: ['unknown-shape'] };

  return validCount
    ? { coords, status: 'valid', warnings: [] }
    : { coords, status: 'invalid', warnings: ['invalid-coordinate-count'] };
}

function buildRegion(token, map, baseUrl, index) {
  const attrs = token.attrs;
  const hrefRaw = attrs.href?.trim() || null;
  const hrefResolved = normalizeDestination(hrefRaw, baseUrl);
  const title = attrs.title?.trim() || null;
  const altPresent = Object.prototype.hasOwnProperty.call(attrs, 'alt');
  const alt = altPresent ? attrs.alt : null;
  const ariaLabel = attrs['aria-label']?.trim() || null;
  const dataOriginalUrlRaw = attrs['data-original-url']?.trim() || null;
  const explicitOriginal = normalizeDestination(dataOriginalUrlRaw, baseUrl);
  const unwrappedOriginal = unwrapWaybackUrl(hrefResolved);
  const classes = (attrs.class || '').split(/\s+/).filter(Boolean).map((value) => value.toLowerCase());
  const isWaybackTarget = Boolean(unwrappedOriginal);
  const isWaybackClass = classes.includes('wayback-replaced');

  let label = null;
  let labelSource = null;
  let labelStatus = 'missing';
  const warnings = [];
  if (ariaLabel) {
    label = ariaLabel;
    labelSource = 'aria-label';
    labelStatus = 'verified-source-label';
  } else if (altPresent && String(alt).trim()) {
    label = String(alt).trim();
    labelSource = 'alt';
    labelStatus = 'verified-source-label';
  } else {
    if (!altPresent) warnings.push('missing-alt');
    else warnings.push('empty-alt');
    if (title) {
      label = title;
      labelSource = 'title';
      labelStatus = 'needs-review';
    } else {
      warnings.push('missing-label');
    }
  }

  if (!hrefRaw) warnings.push('missing-href');
  else if (!hrefResolved) warnings.push('invalid-or-unsafe-href');

  const geometry = validateGeometry(attrs.shape || 'rect', attrs.coords || '');
  warnings.push(...geometry.warnings);

  let destinationStatus = 'original';
  let originalUrl = hrefResolved;
  let archiveUrl = null;
  if (isWaybackTarget || isWaybackClass) {
    destinationStatus = 'archive-replacement';
    archiveUrl = hrefResolved;
    originalUrl = explicitOriginal || unwrappedOriginal;
    if (dataOriginalUrlRaw && !explicitOriginal) warnings.push('invalid-original-url');
    if (!originalUrl) warnings.push('original-url-unavailable');
  } else if (explicitOriginal && explicitOriginal !== hrefResolved) {
    destinationStatus = 'rewritten';
    originalUrl = explicitOriginal;
  }

  return {
    index,
    mapId: map.id,
    mapName: map.name,
    shape: String(attrs.shape || 'rect').trim().toLowerCase(),
    coords: geometry.coords,
    coordsRaw: attrs.coords || '',
    geometryStatus: geometry.status,
    hrefRaw,
    hrefResolved,
    title,
    alt,
    altPresent,
    ariaLabel,
    label,
    labelSource,
    labelStatus,
    classNames: classes,
    dataOriginalUrlRaw,
    originalUrl,
    archiveUrl,
    destinationStatus,
    duplicateDestinationCount: 1,
    warnings: [...new Set(warnings)],
    rawAttributes: { ...attrs },
  };
}

export function summarizeRegions(regions) {
  const items = Array.isArray(regions) ? regions : [];
  return {
    total: items.length,
    verifiedLabels: items.filter((region) => region.labelStatus === 'verified-source-label').length,
    reviewLabels: items.filter((region) => region.labelStatus === 'needs-review').length,
    missingLabels: items.filter((region) => region.labelStatus === 'missing').length,
    archiveReplacements: items.filter((region) => region.destinationStatus === 'archive-replacement').length,
    duplicateDestinations: items.filter((region) => region.duplicateDestinationCount > 1).length,
    geometryWarnings: items.filter((region) => region.geometryStatus === 'invalid').length,
  };
}

export function parseImageMaps(html, options = {}) {
  const requestedBaseUrl = String(options.baseUrl ?? '').trim();
  const baseUrl = requestedBaseUrl ? normalizeDestination(requestedBaseUrl) : null;
  const tokens = tokenizeTags(html);
  const maps = [];
  const images = [];
  const regions = [];
  const diagnostics = [];
  if (requestedBaseUrl && !baseUrl) {
    diagnostics.push({ code: 'invalid-base-url', message: 'The supplied page URL is not a safe absolute HTTP(S) address; relative destinations cannot be resolved.' });
  }
  let currentMap = null;
  let regionIndex = 0;

  for (const token of tokens) {
    if (token.name === 'map') {
      if (token.closing) {
        currentMap = null;
      } else {
        const id = token.attrs.id?.trim() || token.attrs.name?.trim() || `map-${maps.length + 1}`;
        currentMap = {
          id,
          name: token.attrs.name?.trim() || null,
          imageRefs: [],
          regionIndexes: [],
        };
        maps.push(currentMap);
      }
      continue;
    }

    if (token.closing) continue;
    if (token.name === 'img') {
      const width = Number(token.attrs.width);
      const height = Number(token.attrs.height);
      images.push({
        src: token.attrs.src || null,
        alt: token.attrs.alt ?? null,
        width: Number.isFinite(width) && width > 0 ? width : null,
        height: Number.isFinite(height) && height > 0 ? height : null,
        usemap: token.attrs.usemap?.replace(/^#/, '') || null,
        rawAttributes: { ...token.attrs },
      });
      continue;
    }

    if (token.name === 'area') {
      regionIndex += 1;
      const mapContext = currentMap || { id: null, name: null };
      const region = buildRegion(token, mapContext, baseUrl, regionIndex);
      if (currentMap) {
        currentMap.regionIndexes.push(regionIndex);
      } else {
        region.warnings.push('area-outside-map');
        diagnostics.push({ code: 'area-outside-map', regionIndex, message: `Area element ${regionIndex} is outside a map element and cannot be spatially associated.` });
      }
      if (!region.hrefRaw) diagnostics.push({ code: 'missing-href', regionIndex, message: `Region ${regionIndex} has no href.` });
      if (!region.label && !region.hrefResolved) diagnostics.push({ code: 'unlabelled-undestinationed-region', regionIndex, message: `Region ${regionIndex} has neither a source label nor a usable destination.` });
      regions.push(region);
    }
  }

  for (const map of maps) {
    for (const image of images) {
      if (image.usemap && (image.usemap === map.id || image.usemap === map.name)) {
        if (image.src) map.imageRefs.push(image.src);
        image.mapId = map.id;
      }
    }
  }

  const destinationCounts = new Map();
  for (const region of regions) {
    const identity = region.originalUrl || region.hrefResolved;
    if (!identity) continue;
    destinationCounts.set(identity, (destinationCounts.get(identity) || 0) + 1);
  }
  for (const region of regions) {
    const identity = region.originalUrl || region.hrefResolved;
    region.duplicateDestinationCount = identity ? (destinationCounts.get(identity) || 1) : 1;
    if (region.duplicateDestinationCount > 1) region.warnings.push('duplicate-destination');
  }

  return {
    provenance: {
      baseUrl,
      parser: 'Old Web Rescue Lab Pixel Atlas parser v0.1',
      networkRequests: 0,
    },
    maps,
    images,
    regions,
    diagnostics,
    summary: summarizeRegions(regions),
  };
}
