/**
 * Environment configuration and safety validation for k6 tests.
 */

const DEFAULT_BASE_URL = 'http://localhost:3333';
const DEFAULT_TIMEOUT = '10s';

const ALLOWED_HOSTS = [
  'localhost',
  '127.0.0.1',
  '0.0.0.0',
  'host.docker.internal',
  'quickpizza',
  'public-api',
];

export function getEnvironmentConfig() {
  const baseUrl = __ENV.BASE_URL || DEFAULT_BASE_URL;
  const timeout = __ENV.REQUEST_TIMEOUT || DEFAULT_TIMEOUT;
  const allowExternal = (__ENV.ALLOW_EXTERNAL_TARGET || 'false').toLowerCase() === 'true';
  const environmentName = __ENV.TEST_ENV || 'local';

  // Safety Allowlist Validation
  validateTargetSafety(baseUrl, allowExternal);

  return {
    environmentName,
    baseUrl: baseUrl.replace(/\/+$/, ''), // strip trailing slash
    timeout,
    allowExternal,
    prometheusRemoteWrite: __ENV.K6_PROMETHEUS_REMOTE_URL || 'http://localhost:9090/api/v1/write',
  };
}

function validateTargetSafety(targetUrl, allowExternal) {
  let hostname;
  try {
    // Extract hostname from URL
    const match = targetUrl.match(/^(?:https?:\/\/)?([^\/:]+)/i);
    hostname = match ? match[1] : '';
  } catch (e) {
    throw new Error(`[SAFETY] Malformed BASE_URL: "${targetUrl}"`);
  }

  const isAllowedLocal = ALLOWED_HOSTS.includes(hostname);

  if (!isAllowedLocal && !allowExternal) {
    throw new Error(
      `[SAFETY VIOLATION] Target host "${hostname}" is NOT on the local allowlist!\n` +
      `High-volume testing against public or external infrastructure is strictly prohibited by default.\n` +
      `If you have explicit written authorization, you must set ALLOW_EXTERNAL_TARGET=true to proceed.`
    );
  }
}
