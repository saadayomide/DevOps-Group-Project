import React from 'react'
import { MemoryRouter } from 'react-router-dom'
import { render } from '@testing-library/react'
import { ShoppingProvider } from '../context/ShoppingContext'

/**
 * Minimal test provider that wraps components for testing
 * Uses MemoryRouter to avoid navigation issues in tests
 */
export function TestProviders({ children, initialEntries = ['/'] }) {
  return (
    <MemoryRouter initialEntries={initialEntries}>
      <ShoppingProvider>
        {children}
      </ShoppingProvider>
    </MemoryRouter>
  )
}

/**
 * Custom render function that wraps component with providers
 */
export function renderWithProviders(ui, options = {}) {
  const { initialEntries, ...renderOptions } = options

  function Wrapper({ children }) {
    return <TestProviders initialEntries={initialEntries}>{children}</TestProviders>
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}
