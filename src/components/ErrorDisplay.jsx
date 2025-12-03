import React from 'react';
import './ErrorDisplay.css';

/**
 * ErrorDisplay Component
 * Displays error messages with retry functionality
 * Handles different error types: 422, network, timeout, validation
 */
const ErrorDisplay = ({ error, onRetry, errorType = 'general' }) => {
  // Determine error category for better UI
  const getErrorCategory = () => {
    if (!error) return 'general';

    const errorLower = error.toLowerCase();

    // Network errors
    if (errorLower.includes('network') || errorLower.includes('connection')) {
      return 'network';
    }

    // Timeout errors
    if (errorLower.includes('timeout')) {
      return 'timeout';
    }

    // Validation errors (422)
    if (errorLower.includes('validation') || errorLower.includes('unprocessable')) {
      return 'validation';
    }

    // Bad request (400)
    if (errorLower.includes('bad request') || errorLower.includes('cannot be empty')) {
      return 'validation';
    }

    // Not found (404)
    if (errorLower.includes('not found')) {
      return 'notfound';
    }

    return errorType || 'general';
  };

  const category = getErrorCategory();

  const getErrorIcon = () => {
    switch (category) {
      case 'network':
        return '📡';
      case 'timeout':
        return '⏱️';
      case 'validation':
        return '⚠️';
      case 'notfound':
        return '🔍';
      default:
        return '❌';
    }
  };

  const getErrorTitle = () => {
    switch (category) {
      case 'network':
        return 'Connection Error';
      case 'timeout':
        return 'Request Timeout';
      case 'validation':
        return 'Invalid Input';
      case 'notfound':
        return 'Not Found';
      default:
        return 'Error';
    }
  };

  const getErrorSuggestion = () => {
    switch (category) {
      case 'network':
        return 'Please check your internet connection and try again.';
      case 'timeout':
        return 'The request took too long. Please try again.';
      case 'validation':
        return 'Please check your input and try again.';
      case 'notfound':
        return 'The requested resource was not found.';
      default:
        return 'An unexpected error occurred. Please try again.';
    }
  };

  return (
    <div className={`error-display error-${category}`}>
      <div className="error-icon">{getErrorIcon()}</div>
      <h3 className="error-title">{getErrorTitle()}</h3>
      <p className="error-message">{error}</p>
      <p className="error-suggestion">{getErrorSuggestion()}</p>
      {onRetry && (
        <button onClick={onRetry} className="error-retry-button">
          Retry
        </button>
      )}
    </div>
  );
};

export default ErrorDisplay;
