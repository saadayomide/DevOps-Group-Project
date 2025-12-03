import React from 'react'

/**
 * LoadingIndicator Component
 * Displays a loading state when isLoading prop is true
 *
 * @param {boolean} isLoading - Whether to show the loading indicator
 * @param {string} message - Optional custom loading message
 */
export default function LoadingIndicator({ isLoading, message = 'Loading...' }) {
  if (!isLoading) return null

  return (
    <div className="loading-indicator">
      <div className="loading-spinner"></div>
      <span className="loading-message">{message}</span>
    </div>
  )
}
