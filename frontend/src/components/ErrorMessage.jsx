import React from 'react'

/**
 * ErrorMessage Component
 * Displays error messages when message prop is provided
 *
 * @param {string} message - Error message to display (null/empty hides component)
 * @param {string} type - Error type: 'error' (default) or 'warning'
 */
export default function ErrorMessage({ message, type = 'error' }) {
  if (!message) return null

  return (
    <div className={`alert ${type}`} role="alert">
      <span className="error-icon">⚠️</span>
      <span className="error-text">{message}</span>
    </div>
  )
}
