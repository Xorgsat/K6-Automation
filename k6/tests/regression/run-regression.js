/**
 * Performance Regression Test Runner.
 * Executes a deterministic 15 VU workload for baseline comparison.
 */

import exec from 'k6/execution';
import { HttpClient } from '../../lib/http-client.js';
import { getEnvironmentConfig } from '../../config/environment.js';
import { getWorkloadProfile, buildK6Scenario } from '../../config/workloads.js';
import { getThresholdsForProfile } from '../../config/thresholds.js';
import { runMixedUserJourney } from '../../scenarios/mixed-user-journey.js';

const workload = getWorkloadProfile('regression');
const thresholds = getThresholdsForProfile('regression');

export const options = {
  scenarios: buildK6Scenario('regression', 'regressionJourney'),
  thresholds: thresholds,
  setupTimeout: '30s',
  teardownTimeout: '30s',
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

export function regressionJourney(data) {
  const client = new HttpClient({ baseUrl: data.baseUrl });
  const vuIndex = exec.vu && exec.vu.idInTest ? exec.vu.idInTest - 1 : 0;
  runMixedUserJourney(client, vuIndex, data.workload);
}

export default regressionJourney;

export function handleSummary(data) {
  const summaryFileName = __ENV.SUMMARY_OUTPUT || 'results/raw/regression-summary.json';
  const output = {};
  output[summaryFileName] = JSON.stringify(data, null, 2);
  return output;
}
