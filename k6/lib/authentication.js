/**
 * Authentication and User Session Manager for QuickPizza.
 * 
 * Uses the 100 pre-seeded load testing accounts (user1-user100)
 * to avoid CPU saturation on bcrypt password hashing during load tests.
 */

import exec from 'k6/execution';

// 100 seeded load test tokens from QuickPizza migrations:
// user1 -> loadtestuser0004 ... user100 -> loadtestuser0103
const SEEDED_TOKENS = [];
for (let i = 4; i <= 103; i++) {
  const padded = i.toString().padStart(4, '0');
  SEEDED_TOKENS.push(`loadtestuser${padded}`);
}

const DEFAULT_ADMIN_TOKEN = 'abcdef0123456789';

export function getVuToken(vuIndex) {
  const index = vuIndex !== undefined 
    ? vuIndex 
    : (exec.vu && exec.vu.idInTest ? exec.vu.idInTest - 1 : 0);

  if (index < 0 || SEEDED_TOKENS.length === 0) {
    return DEFAULT_ADMIN_TOKEN;
  }

  return SEEDED_TOKENS[index % SEEDED_TOKENS.length];
}

export function getAuthHeaders(vuIndex) {
  const token = getVuToken(vuIndex);
  return {
    'Authorization': `Token ${token}`,
  };
}

export function getDefaultToken() {
  return DEFAULT_ADMIN_TOKEN;
}
