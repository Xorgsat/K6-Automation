/**
 * Reusable functional and structural assertion helpers for k6.
 */

import { check } from 'k6';
import { recordValidationError } from './metrics.js';

export function checkStatus(res, expectedStatus, label) {
  const checkName = label || `status is ${expectedStatus}`;
  const passed = check(res, {
    [checkName]: (r) => r && r.status === expectedStatus,
  });

  if (!passed) {
    recordValidationError();
  }
  return passed;
}

export function checkPizzaRecommendation(res) {
  const passed = check(res, {
    'recommendation status is 200': (r) => r.status === 200,
    'recommendation has pizza object': (r) => {
      try {
        const json = r.json();
        return json && json.pizza && typeof json.pizza.name === 'string';
      } catch (e) {
        return false;
      }
    },
    'recommendation has valid ingredients': (r) => {
      try {
        const json = r.json();
        return Array.isArray(json.pizza.ingredients) && json.pizza.ingredients.length > 0;
      } catch (e) {
        return false;
      }
    },
    'recommendation has calories': (r) => {
      try {
        const json = r.json();
        return typeof json.calories === 'number' && json.calories > 0;
      } catch (e) {
        return false;
      }
    },
  });

  if (!passed) {
    recordValidationError();
  }
  return passed;
}

export function checkIngredients(res, ingredientType) {
  const passed = check(res, {
    [`ingredients (${ingredientType}) status is 200`]: (r) => r.status === 200,
    [`ingredients (${ingredientType}) has list`]: (r) => {
      try {
        const json = r.json();
        return Array.isArray(json.ingredients) && json.ingredients.length > 0;
      } catch (e) {
        return false;
      }
    },
  });

  if (!passed) {
    recordValidationError();
  }
  return passed;
}

export function checkDoughs(res) {
  const passed = check(res, {
    'doughs status is 200': (r) => r.status === 200,
    'doughs has list': (r) => {
      try {
        const json = r.json();
        return Array.isArray(json.doughs) && json.doughs.length > 0;
      } catch (e) {
        return false;
      }
    },
  });

  if (!passed) {
    recordValidationError();
  }
  return passed;
}

export function checkTools(res) {
  const passed = check(res, {
    'tools status is 200': (r) => r.status === 200,
    'tools has list': (r) => {
      try {
        const json = r.json();
        return Array.isArray(json.tools) && json.tools.length > 0;
      } catch (e) {
        return false;
      }
    },
  });

  if (!passed) {
    recordValidationError();
  }
  return passed;
}

export function checkRatingCreated(res) {
  const passed = check(res, {
    'rating created status is 201': (r) => r.status === 201,
    'rating created has id': (r) => {
      try {
        const json = r.json();
        return json && json.id !== undefined;
      } catch (e) {
        return false;
      }
    },
  });

  if (!passed) {
    recordValidationError();
  }
  return passed;
}
