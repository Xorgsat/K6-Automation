/**
 * Mixed User Journey Orchestrator.
 * Selects journeys dynamically based on weighted distribution configured in workloads.json.
 */

import { selectWeightedJourney } from '../lib/helpers.js';
import { runRecommendationJourney } from './recommendation.js';
import { runCatalogJourney } from './catalog.js';
import { runRatingsJourney } from './ratings.js';
import { runHealthJourney } from './health.js';

export function runMixedUserJourney(client, vuIndex, workloadConfig) {
  const distribution = workloadConfig ? workloadConfig.journeyDistribution : null;
  const thinkTime = workloadConfig ? workloadConfig.thinkTime : null;

  const selectedJourney = selectWeightedJourney(distribution);

  switch (selectedJourney) {
    case 'recommendation':
      runRecommendationJourney(client, vuIndex, thinkTime);
      break;
    case 'catalog':
      runCatalogJourney(client, vuIndex, thinkTime);
      break;
    case 'ratings':
      runRatingsJourney(client, vuIndex, thinkTime);
      break;
    case 'health':
      runHealthJourney(client, thinkTime);
      break;
    default:
      runRecommendationJourney(client, vuIndex, thinkTime);
      break;
  }
}
