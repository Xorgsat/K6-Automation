/**
 * Master k6 execution runner for QuickPizza Performance Framework.
 * Driven entirely by config/workloads.json, config/thresholds.json, and environments.
 */

import exec from 'k6/execution';
import { HttpClient } from '../lib/http-client.js';
import { getEnvironmentConfig } from '../config/environment.js';
import { getWorkloadProfile, buildK6Scenario } from '../config/workloads.js';
import { getThresholdsForProfile } from '../config/thresholds.js';
import { runMixedUserJourney } from '../scenarios/mixed-user-journey.js';

const targetProfile = __ENV.WORKLOAD_PROFILE || 'smoke';
const workload = getWorkloadProfile(targetProfile);
const thresholds = getThresholdsForProfile(targetProfile);

export const options = {
  scenarios: buildK6Scenario(targetProfile, 'runJourney'),
  thresholds: thresholds,
  setupTimeout: '30s',
  teardownTimeout: '30s',
};

export function setup() {
  const env = getEnvironmentConfig();
  const client = new HttpClient({ baseUrl: env.baseUrl });

  // Verify readiness before starting
  const ready = client.get('/ready', { name: '/ready' });
  if (ready.status !== 200) {
    throw new Error(`[SETUP FAILED] Target ${env.baseUrl} failed readiness probe (HTTP ${ready.status})`);
  }

  return {
    profile: targetProfile,
    baseUrl: env.baseUrl,
    startTime: new Date().toISOString(),
    workload: workload,
  };
}

export function runJourney(data) {
  const client = new HttpClient({ baseUrl: data.baseUrl });
  const vuIndex = exec.vu && exec.vu.idInTest ? exec.vu.idInTest - 1 : 0;
  runMixedUserJourney(client, vuIndex, data.workload);
}

export default runJourney;

export function teardown(data) {
  // Teardown log
}

export function handleSummary(data) {
  const summaryFileName = __ENV.SUMMARY_OUTPUT || 'summary.json';

  const output = {};
  output[summaryFileName] = JSON.stringify(data, null, 2);

  return output;
}
