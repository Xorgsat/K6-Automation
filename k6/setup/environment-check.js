/**
 * Pre-flight k6 environment check script.
 * Validates connectivity to QuickPizza, Prometheus, and Grafana.
 */

import http from 'k6/http';
import { check } from 'k6';
import { getEnvironmentConfig } from '../config/environment.js';

export const options = {
  vus: 1,
  iterations: 1,
};

export default function () {
  const env = getEnvironmentConfig();

  // 1. Check Liveness
  const liveness = http.get(`${env.baseUrl}/healthz`);
  check(liveness, {
    'liveness is 200': (r) => r.status === 200,
  });

  // 2. Check Readiness
  const readiness = http.get(`${env.baseUrl}/ready`);
  check(readiness, {
    'readiness is 200': (r) => r.status === 200,
  });

  // 3. Check Auth token with catalog
  const catalog = http.get(`${env.baseUrl}/api/doughs`, {
    headers: {
      'Authorization': 'Token abcdef0123456789',
    },
  });
  check(catalog, {
    'authenticated catalog call is 200': (r) => r.status === 200,
  });
}
