import { DEFAULT_SYMBOLS, createGame, flipCard, hideMismatched } from './game-engine.mjs';

const CARD_META = {
  satellite: { label: 'Satellite', icon: '🛰️' },
  planet: { label: 'Planet', icon: '🪐' },
  cassette: { label: 'Cassette', icon: '📼' },
  gamepad: { label: 'Game controller', icon: '🎮' },
  star: { label: 'Star', icon: '🌟' },
  disk: { label: 'Floppy disk', icon: '💾' },
  puzzle: { label: 'Puzzle piece', icon: '🧩' },
  rocket: { label: 'Rocket', icon: '🚀' },
};

const grid = document.querySelector('#game-grid');
const movesOutput = document.querySelector('#moves');
const pairsOutput = document.querySelector('#pairs');
const progressLabel = document.querySelector('#progress-label');
const progressBar = document.querySelector('#progress-bar');
const progressFill = document.querySelector('#progress-fill');
const status = document.querySelector('#game-status');
const newGameButton = document.querySelector('#new-game');

let state = createGame();
let mismatchTimer = null;

function getCardDescription(card, index) {
  const meta = CARD_META[card.pairId];
  if (state.matched.includes(index)) return `${meta.label}, matched`;
  if (state.flipped.includes(index)) return `${meta.label}, revealed`;
  return `Hidden card ${index + 1}`;
}

function updateCardElements() {
  const buttons = grid.querySelectorAll('.memory-card');
  buttons.forEach((button, index) => {
    const card = state.cards[index];
    const isMatched = state.matched.includes(index);
    const isOpen = isMatched || state.flipped.includes(index);
    const meta = CARD_META[card.pairId];
    button.classList.toggle('is-open', isOpen && !isMatched);
    button.classList.toggle('is-matched', isMatched);
    button.setAttribute('aria-label', getCardDescription(card, index));
    button.setAttribute('aria-pressed', String(isOpen));
    button.setAttribute('aria-disabled', String(isMatched));
    button.querySelector('.card-mark').textContent = isOpen ? meta.icon : '?';
  });
}

function updateStats() {
  const pairsFound = state.matched.length / 2;
  const percent = Math.round((pairsFound / DEFAULT_SYMBOLS.length) * 100);
  movesOutput.textContent = String(state.moves);
  pairsOutput.textContent = `${pairsFound} / ${DEFAULT_SYMBOLS.length}`;
  progressLabel.textContent = `${percent}%`;
  progressBar.setAttribute('aria-valuenow', String(pairsFound));
  progressFill.style.width = `${percent}%`;
}

function announce(message) {
  status.textContent = message;
}

function buildBoard() {
  const fragment = document.createDocumentFragment();
  state.cards.forEach((card, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'memory-card';
    button.dataset.index = String(index);
    button.setAttribute('aria-label', `Hidden card ${index + 1}`);
    button.setAttribute('aria-pressed', 'false');
    button.setAttribute('aria-disabled', 'false');
    button.innerHTML = '<span class="card-mark" aria-hidden="true">?</span>';
    button.addEventListener('click', () => chooseCard(index));
    fragment.append(button);
  });
  grid.replaceChildren(fragment);
  updateCardElements();
  updateStats();
}

function chooseCard(index) {
  const previous = state;
  state = flipCard(state, index);
  if (state === previous) return;

  updateCardElements();
  updateStats();

  if (state.complete) {
    announce(`All eight pairs found in ${state.moves} moves. Recovered!`);
    return;
  }

  if (state.matched.length > previous.matched.length) {
    const matchedIndex = state.matched[state.matched.length - 1];
    const label = CARD_META[state.cards[matchedIndex].pairId].label;
    announce(`Match found: ${label}. ${state.matched.length / 2} of 8 pairs found.`);
  } else if (state.flipped.length === 2) {
    announce('Not a match. Both cards will turn over shortly.');
    window.clearTimeout(mismatchTimer);
    mismatchTimer = window.setTimeout(() => {
      state = hideMismatched(state);
      updateCardElements();
      announce('Cards turned back over. Try another pair.');
    }, 900);
  } else {
    const label = CARD_META[state.cards[index].pairId].label;
    announce(`${label} revealed. Choose one more card.`);
  }
}

function startNewGame() {
  window.clearTimeout(mismatchTimer);
  state = createGame();
  buildBoard();
  announce('New game ready. Find all eight pairs.');
}

newGameButton.addEventListener('click', () => {
  startNewGame();
  newGameButton.focus();
});

buildBoard();
