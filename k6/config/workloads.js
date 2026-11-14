/**
 * Workload configuration loader and k6 scenario generator.
 */

const rawWorkloads = JSON.parse(open('../../config/workloads.json'));

export function getWorkloadProfile(profileName) {
  const selectedName = profileName || __ENV.WORKLOAD_PROFILE || 'smoke';
  const profile = rawWorkloads.profiles[selectedName];

  if (!profile) {
    throw new Error(`[CONFIG] Unknown workload profile "${selectedName}". Available: ${Object.keys(rawWorkloads.profiles).join(', ')}`);
  }

  return {
    name: selectedName,
    ...profile,
  };
}

export function buildK6Scenario(profileName, execFunctionName = 'default') {
  const profile = getWorkloadProfile(profileName);

  if (profile.executor === 'constant-vus') {
    return {
      [profile.name]: {
        executor: 'constant-vus',
        vus: profile.vus,
        duration: profile.duration,
        exec: execFunctionName,
      },
    };
  }

  if (profile.executor === 'ramping-vus') {
    return {
      [profile.name]: {
        executor: 'ramping-vus',
        stages: profile.stages,
        exec: execFunctionName,
      },
    };
  }

  throw new Error(`[CONFIG] Unsupported executor "${profile.executor}" in profile "${profile.name}"`);
}
