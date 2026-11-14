/**
 * Centralized custom metrics and error classification counters for k6.
 */

import { Trend, Counter, Rate } from 'k6/metrics';

// Business Transaction Latency Trends
export const recommendationDuration = new Trend('recommendation_duration', true);
export const ratingDuration = new Trend('rating_operation_duration', true);
export const catalogDuration = new Trend('catalog_operation_duration', true);

// Business Success & Failure Rates
export const businessTransactionFailures = new Counter('business_transaction_failures');
export const businessTransactionSuccess = new Rate('business_transaction_success');

// Error Classification Taxonomy
export const errorsTransport = new Counter('errors_transport');
export const errorsClient4xx = new Counter('errors_client_4xx');
export const errorsServer5xx = new Counter('errors_server_5xx');
export const errorsValidation = new Counter('errors_validation');

export function recordHttpOutcome(res) {
  if (!res || res.status === 0) {
    errorsTransport.add(1);
    businessTransactionFailures.add(1);
    businessTransactionSuccess.add(0);
    return;
  }

  if (res.status >= 500) {
    errorsServer5xx.add(1);
    businessTransactionFailures.add(1);
    businessTransactionSuccess.add(0);
    return;
  }

  if (res.status >= 400) {
    errorsClient4xx.add(1);
    businessTransactionFailures.add(1);
    businessTransactionSuccess.add(0);
    return;
  }

  // HTTP success
  businessTransactionSuccess.add(1);
}

export function recordValidationError() {
  errorsValidation.add(1);
  businessTransactionFailures.add(1);
}
