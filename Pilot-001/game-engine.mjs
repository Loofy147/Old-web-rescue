export const DEFAULT_SYMBOLS = Object.freeze([
  'satellite',
  'planet',
  'cassette',
  'gamepad',
  'star',
  'disk',
  'puzzle',
  'rocket',
]);

/** Create a shuffled deck and a fresh, immutable-by-convention game state. */
export function createGame(symbols = DEFAULT_SYMBOLS, random = Math.random) {
  if (!Array.isArray(symbols) || symbols.length < 2) {
    throw new TypeError('Provide at least two unique symbols.');
  }
  if (new Set(symbols).size !== symbols.length) {
    throw new TypeError('Symbols must be unique.');
  }
  if (symbols.some((symbol) => typeof symbol !== 'string' || !symbol.trim())) {
    throw new TypeError('Every symbol must be a non-empty string.');
  }
  if (typeof random !== 'function') {
    throw new TypeError('The random source must be a function.');
  }

  const cards = symbols.flatMap((pairId) => [
    { id: `${pairId}-a`, pairId, label: pairId },
    { id: `${pairId}-b`, pairId, label: pairId },
  ]);

  // Fisher–Yates shuffle. An injected random source keeps tests deterministic.
  for (let i = cards.length - 1; i > 0; i -= 1) {
    const sample = random();
    if (!Number.isFinite(sample) || sample < 0 || sample >= 1) {
      throw new RangeError('The random source must return a number in [0, 1).');
    }
    const j = Math.floor(sample * (i + 1));
    [cards[i], cards[j]] = [cards[j], cards[i]];
  }

  return {
    cards,
    flipped: [],
    matched: [],
    moves: 0,
    complete: false,
  };
}

/** Reveal a card. Matching pairs are recorded immediately; mismatches stay visible. */
export function flipCard(state, index) {
  if (
    !state ||
    !Number.isInteger(index) ||
    index < 0 ||
    index >= state.cards.length ||
    state.complete ||
    state.flipped.length >= 2 ||
    state.flipped.includes(index) ||
    state.matched.includes(index)
  ) {
    return state;
  }

  const flipped = [...state.flipped, index];
  if (flipped.length < 2) {
    return { ...state, flipped };
  }

  const [first, second] = flipped;
  const moves = state.moves + 1;
  if (state.cards[first].pairId !== state.cards[second].pairId) {
    return { ...state, flipped, moves };
  }

  const matched = [...state.matched, first, second];
  return {
    ...state,
    flipped: [],
    matched,
    moves,
    complete: matched.length === state.cards.length,
  };
}

/** Hide only a pending, non-matching pair. */
export function hideMismatched(state) {
  if (!state || state.flipped.length !== 2) return state;
  const [first, second] = state.flipped;
  if (state.cards[first].pairId === state.cards[second].pairId) return state;
  return { ...state, flipped: [] };
}
