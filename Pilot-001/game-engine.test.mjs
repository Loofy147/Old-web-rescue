import test from 'node:test';
import assert from 'node:assert/strict';
import { createGame, flipCard, hideMismatched } from './game-engine.mjs';

const fixedRandom = () => 0;

test('creates two cards per unique symbol and starts clean', () => {
  const game = createGame(['satellite', 'planet', 'cassette'], fixedRandom);
  assert.equal(game.cards.length, 6);
  for (const symbol of ['satellite', 'planet', 'cassette']) {
    assert.equal(game.cards.filter(card => card.pairId === symbol).length, 2);
  }
  assert.deepEqual(game.flipped, []);
  assert.deepEqual(game.matched, []);
  assert.equal(game.moves, 0);
  assert.equal(game.complete, false);
});

test('rejects an unusable symbol set and an invalid random source', () => {
  assert.throws(() => createGame(['only-one']), /at least two unique symbols/i);
  assert.throws(() => createGame(['same', 'same']), /unique/i);
  assert.throws(() => createGame(['a', 'b'], () => 1), /random source/i);
});

test('keeps a mismatched pair visible until it is dismissed and blocks a third card', () => {
  const game = createGame(['satellite', 'planet', 'cassette'], fixedRandom);
  const first = 0;
  const second = game.cards.findIndex((card, index) => index !== first && card.pairId !== game.cards[first].pairId);
  const third = game.cards.findIndex((card, index) => index !== first && index !== second);

  const oneOpen = flipCard(game, first);
  assert.deepEqual(oneOpen.flipped, [first]);
  const mismatch = flipCard(oneOpen, second);
  assert.deepEqual(mismatch.flipped, [first, second]);
  assert.equal(mismatch.moves, 1);
  assert.equal(flipCard(mismatch, third), mismatch);

  const dismissed = hideMismatched(mismatch);
  assert.deepEqual(dismissed.flipped, []);
  assert.equal(dismissed.moves, 1);
  assert.deepEqual(flipCard(dismissed, third).flipped, [third]);
});

test('marks a matching pair and completes a one-pair game', () => {
  const game = createGame(['satellite', 'planet'], fixedRandom);
  const first = 0;
  const second = game.cards.findIndex((card, index) => index !== first && card.pairId === game.cards[first].pairId);
  const oneOpen = flipCard(game, first);
  const solved = flipCard(oneOpen, second);
  assert.deepEqual(solved.matched.sort(), [first, second].sort());
  assert.deepEqual(solved.flipped, []);
  assert.equal(solved.moves, 1);
  assert.equal(solved.complete, false);
  const otherPair = game.cards.findIndex((card, index) => !solved.matched.includes(index));
  const finalPair = game.cards.findIndex((card, index) => index !== otherPair && !solved.matched.includes(index) && card.pairId === game.cards[otherPair].pairId);
  const completed = flipCard(flipCard(solved, otherPair), finalPair);
  assert.equal(completed.complete, true);
  assert.equal(completed.moves, 2);
});

test('does not allow matched cards or invalid positions to be replayed', () => {
  const game = createGame(['satellite', 'planet'], fixedRandom);
  const mate = game.cards.findIndex((card, index) => index !== 0 && card.pairId === game.cards[0].pairId);
  const solved = flipCard(flipCard(game, 0), mate);
  assert.equal(flipCard(solved, 0), solved);
  assert.equal(flipCard(solved, -1), solved);
  assert.equal(flipCard(solved, 99), solved);
});

test('does not hide a single open card or a correctly matched pair', () => {
  const game = createGame(['satellite', 'planet'], fixedRandom);
  const oneOpen = flipCard(game, 0);
  assert.equal(hideMismatched(oneOpen), oneOpen);
  const pairIndex = game.cards.findIndex((card, index) => index !== 0 && card.pairId === game.cards[0].pairId);
  const solved = flipCard(oneOpen, pairIndex);
  assert.equal(hideMismatched(solved), solved);
});
