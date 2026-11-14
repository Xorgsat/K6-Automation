/**
 * Journey D: System Health, Readiness, and Prometheus Telemetry
 */

import { checkStatus } from '../lib/checks.js';
import { stochasticSleep } from '../lib/helpers.js';

export function runHealthJourney(client, thinkTimeConfig) {
  const minSleep = thinkTimeConfig ? thinkTimeConfig.minSeconds : 0.5;
  const maxSleep = thinkTimeConfig ? thinkTimeConfig.maxSeconds : 1.0;

  // 1. Liveness check
  const healthRes = client.get('/healthz', {
    name: '/healthz',
  });
  checkStatus(healthRes, 200, 'liveness probe is 200');

  // 2. Readiness check
  const readyRes = client.get('/ready', {
    name: '/ready',
  });
  checkStatus(readyRes, 200, 'readiness probe is 200');

  stochasticSleep(minSleep, maxSleep);

  // 3. Prometheus metrics endpoint
  const metricsRes = client.get('/metrics', {
    name: '/metrics',
  });
  checkStatus(metricsRes, 200, 'prometheus scrape is 200');
}
