/**
 * Journey C: Pizza Rating Lifecycle (State-Changing, CRUD Operations with Hygiene Cleanup)
 */

import { checkStatus, checkRatingCreated } from '../lib/checks.js';
import { getAuthHeaders } from '../lib/authentication.js';
import { getRandomRating, getRandomRestrictions } from '../lib/test-data.js';
import { stochasticSleep } from '../lib/helpers.js';
import { ratingDuration } from '../lib/metrics.js';

export function runRatingsJourney(client, vuIndex, thinkTimeConfig) {
  const authHeaders = getAuthHeaders(vuIndex);
  const minSleep = thinkTimeConfig ? thinkTimeConfig.minSeconds : 0.5;
  const maxSleep = thinkTimeConfig ? thinkTimeConfig.maxSeconds : 1.5;

  // 1. Generate a recommendation to obtain a valid pizza ID
  const restrictions = getRandomRestrictions();
  const pizzaRes = client.post('/api/pizza', restrictions, {
    name: '/api/pizza',
    headers: authHeaders,
  });

  if (pizzaRes.status !== 200) return;
  const pizzaJson = pizzaRes.json();
  const pizzaId = pizzaJson.pizza && pizzaJson.pizza.id ? pizzaJson.pizza.id : 1;

  stochasticSleep(minSleep, maxSleep);

  // 2. Submit Rating
  const startTime = Date.now();
  const ratingPayload = getRandomRating(pizzaId);

  const postRatingRes = client.post('/api/ratings', ratingPayload, {
    name: '/api/ratings',
    headers: authHeaders,
  });

  const durationMs = Date.now() - startTime;
  ratingDuration.add(durationMs);

  const createdOk = checkRatingCreated(postRatingRes);
  if (!createdOk) return;

  const ratingId = postRatingRes.json().id;

  stochasticSleep(minSleep, maxSleep);

  // 3. Retrieve Created Rating
  const getRatingRes = client.get(`/api/ratings/${ratingId}`, {
    name: '/api/ratings/{id}',
    headers: authHeaders,
  });
  checkStatus(getRatingRes, 200, 'get rating is 200');

  // 4. Update Rating
  const updatePayload = { stars: 5 };
  const putRatingRes = client.put(`/api/ratings/${ratingId}`, updatePayload, {
    name: '/api/ratings/{id}',
    headers: authHeaders,
  });
  checkStatus(putRatingRes, 200, 'update rating is 200');

  // 5. Cleanup: Delete Rating to prevent database bloat
  const delRatingRes = client.del(`/api/ratings/${ratingId}`, {
    name: '/api/ratings/{id}',
    headers: authHeaders,
  });
  checkStatus(delRatingRes, 204, 'delete rating is 204');
}
