/**
 * HTTP Client abstraction for k6.
 * Enforces uniform request tagging, correlation IDs, and error recording.
 */

import http from 'k6/http';
import { recordHttpOutcome } from './metrics.js';
import { getEnvironmentConfig } from '../config/environment.js';

export class HttpClient {
  constructor(customConfig = {}) {
    const envConfig = getEnvironmentConfig();
    this.baseUrl = customConfig.baseUrl || envConfig.baseUrl;
    this.defaultTimeout = customConfig.timeout || envConfig.timeout;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'User-Agent': 'k6-performance-engineering-framework/1.0',
      ...(customConfig.headers || {}),
    };
  }

  _generateCorrelationId() {
    return 'k6-' + Math.random().toString(36).substring(2, 10) + '-' + Date.now().toString(36);
  }

  _buildParams(path, options = {}) {
    const headers = Object.assign(
      {},
      this.defaultHeaders,
      { 'X-Correlation-ID': this._generateCorrelationId() },
      options.headers || {}
    );

    // Bounded metric tag name to prevent high-cardinality label explosion in Prometheus
    const tagName = options.name || path;

    return {
      headers: headers,
      timeout: options.timeout || this.defaultTimeout,
      tags: Object.assign({ name: tagName }, options.tags || {}),
    };
  }

  get(path, options = {}) {
    const url = `${this.baseUrl}${path}`;
    const params = this._buildParams(path, options);
    const res = http.get(url, params);
    recordHttpOutcome(res);
    return res;
  }

  post(path, body = {}, options = {}) {
    const url = `${this.baseUrl}${path}`;
    const payload = typeof body === 'string' ? body : JSON.stringify(body);
    const params = this._buildParams(path, options);
    const res = http.post(url, payload, params);
    recordHttpOutcome(res);
    return res;
  }

  put(path, body = {}, options = {}) {
    const url = `${this.baseUrl}${path}`;
    const payload = typeof body === 'string' ? body : JSON.stringify(body);
    const params = this._buildParams(path, options);
    const res = http.put(url, payload, params);
    recordHttpOutcome(res);
    return res;
  }

  patch(path, body = {}, options = {}) {
    const url = `${this.baseUrl}${path}`;
    const payload = typeof body === 'string' ? body : JSON.stringify(body);
    const params = this._buildParams(path, options);
    const res = http.patch(url, payload, params);
    recordHttpOutcome(res);
    return res;
  }

  del(path, options = {}) {
    const url = `${this.baseUrl}${path}`;
    const params = this._buildParams(path, options);
    const res = http.del(url, null, params);
    recordHttpOutcome(res);
    return res;
  }
}
