/**
 * Journey B: Catalog Browsing (Pure Read-Only, High Throughput)
 */

import { checkDoughs, checkTools, checkIngredients, checkStatus } from '../lib/checks.js';
import { getAuthHeaders } from '../lib/authentication.js';
import { stochasticSleep } from '../lib/helpers.js';
import { catalogDuration } from '../lib/metrics.js';

export function runCatalogJourney(client, vuIndex, thinkTimeConfig) {
  const authHeaders = getAuthHeaders(vuIndex);
  const minSleep = thinkTimeConfig ? thinkTimeConfig.minSeconds : 0.3;
  const maxSleep = thinkTimeConfig ? thinkTimeConfig.maxSeconds : 1.0;

  const startTime = Date.now();

  // 1. Query Doughs
  const doughsRes = client.get('/api/doughs', {
    name: '/api/doughs',
    headers: authHeaders,
  });
  checkDoughs(doughsRes);

  // 2. Query Tools
  const toolsRes = client.get('/api/tools', {
    name: '/api/tools',
    headers: authHeaders,
  });
  checkTools(toolsRes);

  stochasticSleep(minSleep, maxSleep);

  // 3. Query Mozzarellas
  const mozzRes = client.get('/api/ingredients/mozzarella', {
    name: '/api/ingredients/{type}',
    headers: authHeaders,
  });
  checkIngredients(mozzRes, 'mozzarella');

  // 4. Query Quotes
  const quotesRes = client.get('/api/quotes', {
    name: '/api/quotes',
  });
  checkStatus(quotesRes, 200, 'quotes status is 200');

  const durationMs = Date.now() - startTime;
  catalogDuration.add(durationMs);
}
