/**
 * Journey A: Pizza Recommendation Discovery (Read-Heavy, Core Business Flow)
 */

import { checkPizzaRecommendation, checkIngredients, checkDoughs, checkStatus } from '../lib/checks.js';
import { getAuthHeaders } from '../lib/authentication.js';
import { getRandomRestrictions } from '../lib/test-data.js';
import { stochasticSleep } from '../lib/helpers.js';
import { recommendationDuration } from '../lib/metrics.js';

export function runRecommendationJourney(client, vuIndex, thinkTimeConfig) {
  const authHeaders = getAuthHeaders(vuIndex);
  const minSleep = thinkTimeConfig ? thinkTimeConfig.minSeconds : 0.5;
  const maxSleep = thinkTimeConfig ? thinkTimeConfig.maxSeconds : 1.5;

  // 1. Fetch available ingredients (requires auth)
  const ingRes = client.get('/api/ingredients/tomato', {
    name: '/api/ingredients/{type}',
    headers: authHeaders,
  });
  checkIngredients(ingRes, 'tomato');

  // 2. Fetch available doughs (requires auth)
  const doughRes = client.get('/api/doughs', {
    name: '/api/doughs',
    headers: authHeaders,
  });
  checkDoughs(doughRes);

  stochasticSleep(minSleep, maxSleep);

  // 3. Post Pizza Recommendation
  const restrictions = getRandomRestrictions();
  const startTime = Date.now();

  const recRes = client.post('/api/pizza', restrictions, {
    name: '/api/pizza',
    headers: authHeaders,
  });

  const durationMs = Date.now() - startTime;
  recommendationDuration.add(durationMs);

  const passed = checkPizzaRecommendation(recRes);
  if (!passed) return;

  const pizzaData = recRes.json();
  const pizzaId = pizzaData.pizza && pizzaData.pizza.id ? pizzaData.pizza.id : null;

  if (pizzaId) {
    stochasticSleep(minSleep, maxSleep);

    // 4. Retrieve saved recommendation
    const getPizzaRes = client.get(`/api/pizza/${pizzaId}`, {
      name: '/api/pizza/{id}',
      headers: authHeaders,
    });
    checkStatus(getPizzaRes, 200, 'fetch saved pizza is 200');
  }
}
