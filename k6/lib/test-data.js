/**
 * Test data synthesis and payload generation for QuickPizza scenarios.
 */

import { randomElement } from './helpers.js';

const INGREDIENTS_POOL = [
  'pepperoni',
  'anchovies',
  'mushrooms',
  'onions',
  'bacon',
  'pineapple',
  'olives',
];

const TOOLS_POOL = [
  'knife',
  'rolling_pin',
  'pizza_cutter',
];

export function getRandomRestrictions() {
  const isVegetarian = Math.random() < 0.3; // 30% chance vegetarian
  const maxCalories = 400 + Math.floor(Math.random() * 600); // 400-1000 cal
  const excludedIngredient = Math.random() < 0.4 ? [randomElement(INGREDIENTS_POOL)] : [];
  const excludedTool = Math.random() < 0.2 ? [randomElement(TOOLS_POOL)] : [];

  return {
    maxCaloriesPerSlice: maxCalories,
    mustBeVegetarian: isVegetarian,
    excludedIngredients: excludedIngredient,
    excludedTools: excludedTool,
    maxNumberOfToppings: 4 + Math.floor(Math.random() * 3),
    minNumberOfToppings: 1 + Math.floor(Math.random() * 2),
  };
}

export function getRandomRating(pizzaId) {
  return {
    pizza_id: pizzaId,
    stars: 1 + Math.floor(Math.random() * 5), // 1 to 5 stars
  };
}
