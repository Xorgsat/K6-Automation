/**
 * Threshold configuration loader and k6 thresholds mapper.
 */

const rawThresholds = JSON.parse(open('../../config/thresholds.json'));

export function getThresholdsForProfile(profileName) {
  const selectedName = profileName || __ENV.WORKLOAD_PROFILE || 'smoke';
  const profileThresholds = rawThresholds.profiles[selectedName];

  if (!profileThresholds) {
    throw new Error(`[CONFIG] Unknown threshold profile "${selectedName}". Available: ${Object.keys(rawThresholds.profiles).join(', ')}`);
  }

  return profileThresholds;
}
