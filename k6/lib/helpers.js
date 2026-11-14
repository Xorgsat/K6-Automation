/**
 * Helpers for stochastic delays, random selections, and weighted routing.
 */

import { sleep } from 'k6';

export function stochasticSleep(minSeconds = 0.5, maxSeconds = 1.5) {
  const delta = maxSeconds - minSeconds;
  const duration = minSeconds + (Math.random() * (delta > 0 ? delta : 0));
  sleep(duration);
}

export function selectWeightedJourney(distribution) {
  const defaultDist = {
    recommendation: 0.60,
    catalog: 0.20,
    ratings: 0.10,
    health: 0.10,
  };

  const dist = distribution || defaultDist;
  const rand = Math.random();
  let cumulative = 0;

  for (const [journey, weight] of Object.entries(dist)) {
    cumulative += weight;
    if (rand <= cumulative) {
      return journey;
    }
  }

  return 'recommendation';
}

export function randomElement(arr) {
  if (!arr || arr.length === 0) return null;
  return arr[Math.floor(Math.random() * arr.length)];
}
