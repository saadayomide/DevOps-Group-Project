import React from 'react';
import './LoadingSpinner.css';

/**
 * LoadingSpinner Component
 * Displays a loading spinner during API calls
 */
const LoadingSpinner = ({ message = 'Loading...' }) => {
  return (
    <div className="loading-spinner-container">
      <div className="loading-spinner" aria-label="Loading">
        <div className="spinner-circle"></div>
        <div className="spinner-circle"></div>
        <div className="spinner-circle"></div>
      </div>
      <p className="loading-message">{message}</p>
    </div>
  );
};

export default LoadingSpinner;
