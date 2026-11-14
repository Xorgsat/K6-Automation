/**
 * Dedicated Smoke Test Runner.
 * Executes a controlled 2 VU, 30s sanity run of the mixed user journey.
 */

import exec from 'k6/execution';
import { HttpClient } from '../../lib/http-client.js';
import { getEnvironmentConfig } from '../../config/environment.js';
import { getWorkloadProfile, buildK6Scenario } from '../../config/workloads.js';
import { getThresholdsForProfile } from '../../config/thresholds.js';
import { runMixedUserJourney } from '../../scenarios/mixed-user-journey.js';

const workload = getWorkloadProfile('smoke');
const thresholds = getThresholdsForProfile('smoke');

export const options = {
  scenarios: buildK6Scenario('smoke', 'smokeJourney'),
  thresholds: thresholds,
  setupTimeout: '30s',
};

export function setup() {
  const env = getEnvironmentConfig();
  const client = new HttpClient({ baseUrl: env.baseUrl });
  const ready = client.get('/ready', { name: '/ready' });
  if (ready.status !== 200) {
    throw new Error(`Target ${env.baseUrl} failed readiness probe`);
  }
  return { baseUrl: env.baseUrl, workload: workload };
}

export function smokeJourney(data) {
  const client = new HttpClient({ baseUrl: data.baseUrl });
  const vuIndex = exec.vu && exec.vu.idInTest ? exec.vu.idInTest - 1 : 0;
  runMixedUserJourney(client, vuIndex, data.workload);
}

export default smokeJourney;

export function handleSummary(data) {
  const summaryFileName = __ENV.SUMMARY_OUTPUT || 'results/raw/smoke-summary.json';
  const output = {};
  output[summaryFileName] = JSON.stringify(data, null, 2);
  return output;
}
