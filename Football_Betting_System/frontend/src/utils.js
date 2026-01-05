/**
 * BULLETPROOF utility functions with comprehensive safety checks
 */

/**
 * Safely format a number to fixed decimal places
 * Returns 'N/A' for any invalid input
 */
export const safeNumber = (value, decimals = 2) => {
  // Check for undefined, null
  if (value === undefined || value === null) {
    return 'N/A';
  }
  
  // Convert to number
  const num = Number(value);
  
  // Check for NaN, Infinity, or -Infinity
  if (!Number.isFinite(num)) {
    return 'N/A';
  }
  
  // Return fixed decimal string
  return num.toFixed(decimals);
};

/**
 * Safely format a decimal as percentage
 * Returns '0.0%' for any invalid input
 */
export const safePercent = (value, decimals = 1) => {
  if (value === undefined || value === null) {
    return '0.0%';
  }
  
  const num = Number(value);
  
  if (!Number.isFinite(num)) {
    return '0.0%';
  }
  
  return (num * 100).toFixed(decimals) + '%';
};

/**
 * Safely get a property from an object with optional chaining
 * Returns defaultValue if property doesn't exist or is invalid
 */
export const safeGet = (obj, path, defaultValue = null) => {
  if (!obj) return defaultValue;
  
  const keys = path.split('.');
  let result = obj;
  
  for (const key of keys) {
    if (result === undefined || result === null) {
      return defaultValue;
    }
    result = result[key];
  }
  
  return result !== undefined && result !== null ? result : defaultValue;
};

/**
 * Safely format a date string
 */
export const safeDate = (dateString) => {
  if (!dateString) return 'TBD';
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'TBD';
    return date.toLocaleDateString();
  } catch {
    return 'TBD';
  }
};

/**
 * Safely format a time string
 */
export const safeTime = (dateString) => {
  if (!dateString) return 'TBD';
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'TBD';
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return 'TBD';
  }
};

/**
 * Safely calculate a product
 */
export const safeMultiply = (a, b, decimals = 2) => {
  const numA = Number(a);
  const numB = Number(b);
  
  if (!Number.isFinite(numA) || !Number.isFinite(numB)) {
    return 'N/A';
  }
  
  const result = numA * numB;
  
  if (!Number.isFinite(result)) {
    return 'N/A';
  }
  
  return result.toFixed(decimals);
};
