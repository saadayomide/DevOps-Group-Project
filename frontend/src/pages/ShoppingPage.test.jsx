/**
 * ShoppingPage Component Tests
 *
 * Tests for Team C's core frontend requirements:
 * - C1: Comparison UI (loading states, error handling, results display)
 * - C2: Shopping list input and store selection
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { ShoppingProvider } from '../context/ShoppingContext'
import ShoppingPage from './ShoppingPage'
import * as api from '../api'

// Mock the API module
vi.mock('../api', () => ({
  fetchSupermarkets: vi.fn(),
  searchProducts: vi.fn(),
  compareBasket: vi.fn(),
  baseUrl: '/api/v1',
}))

const mockSupermarkets = [
  { id: 1, name: 'Mercadona' },
  { id: 2, name: 'Carrefour' },
  { id: 3, name: 'Lidl' },
]

const mockCompareResults = {
  items: [
    { name: 'Leche entera', store: 'Mercadona', price: 0.89 },
  ],
  storeTotals: [
    { store: 'Mercadona', total: 0.89 },
    { store: 'Carrefour', total: 0.95 },
  ],
  priceComparison: [
    {
      name: 'Leche entera',
      cheapestStore: 'Mercadona',
      prices: [
        { store: 'Mercadona', price: 0.89 },
        { store: 'Carrefour', price: 0.95 },
      ],
    },
  ],
  overallTotal: 0.89,
  unmatched: [],
}

function renderShoppingPage() {
  return render(
    <MemoryRouter>
      <ShoppingProvider>
        <ShoppingPage />
      </ShoppingProvider>
    </MemoryRouter>
  )
}

describe('ShoppingPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    api.fetchSupermarkets.mockResolvedValue(mockSupermarkets)
    api.searchProducts.mockResolvedValue([])
    api.compareBasket.mockResolvedValue(mockCompareResults)
  })

  describe('Initial Render and Loading States', () => {
    it('renders shopping list heading', async () => {
      renderShoppingPage()
      expect(screen.getByText('Shopping list')).toBeInTheDocument()
    })

    it('shows loading state while fetching supermarkets', async () => {
      // Delay the API response to see loading state
      api.fetchSupermarkets.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockSupermarkets), 100))
      )

      renderShoppingPage()
      expect(screen.getByText(/loading supermarkets/i)).toBeInTheDocument()

      await waitFor(() => {
        expect(screen.queryByText(/loading supermarkets/i)).not.toBeInTheDocument()
      })
    })

    it('displays supermarkets after loading', async () => {
      renderShoppingPage()

      await waitFor(() => {
        expect(screen.getByText('Mercadona')).toBeInTheDocument()
        expect(screen.getByText('Carrefour')).toBeInTheDocument()
        expect(screen.getByText('Lidl')).toBeInTheDocument()
      })
    })
  })

  describe('Shopping List Management (C2)', () => {
    it('allows adding items to shopping list', async () => {
      const user = userEvent.setup()
      renderShoppingPage()

      await waitFor(() => {
        expect(screen.getByText('Mercadona')).toBeInTheDocument()
      })

      const input = screen.getByPlaceholderText(/type to search/i)
      await user.type(input, 'Leche entera')

      const addButton = screen.getByRole('button', { name: /add/i })
      await user.click(addButton)

      expect(screen.getByText('Leche entera')).toBeInTheDocument()
    })

    it('allows removing items from shopping list', async () => {
      const user = userEvent.setup()
      renderShoppingPage()

      await waitFor(() => {
        expect(screen.getByText('Mercadona')).toBeInTheDocument()
      })

      // Add an item first
      const input = screen.getByPlaceholderText(/type to search/i)
      await user.type(input, 'Pan integral')
      await user.click(screen.getByRole('button', { name: /add/i }))

      expect(screen.getByText('Pan integral')).toBeInTheDocument()

      // Remove the item
      const removeButton = screen.getByRole('button', { name: '×' })
      await user.click(removeButton)

      expect(screen.queryByText('Pan integral')).not.toBeInTheDocument()
    })

    it('allows toggling store selection', async () => {
      const user = userEvent.setup()
      renderShoppingPage()

      await waitFor(() => {
        expect(screen.getByText('Mercadona')).toBeInTheDocument()
      })

      const mercadonaChip = screen.getByRole('button', { name: 'Mercadona' })

      // Initially some stores may be selected
      await user.click(mercadonaChip)

      // Toggle again
      await user.click(mercadonaChip)

      // Verify the button is still there and clickable
      expect(mercadonaChip).toBeInTheDocument()
    })
  })

  describe('Price Comparison (C1)', () => {
    it('disables compare button when list is empty', async () => {
      renderShoppingPage()

      await waitFor(() => {
        expect(screen.getByText('Mercadona')).toBeInTheDocument()
      })

      // Compare button should be disabled when no items in list
      const compareButton = screen.getByRole('button', { name: /compare prices/i })
      expect(compareButton).toBeDisabled()
    })

    it('shows loading state during comparison', async () => {
      const user = userEvent.setup()

      // Delay the comparison response
      api.compareBasket.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockCompareResults), 200))
      )

      renderShoppingPage()

      await waitFor(() => {
        expect(screen.getByText('Mercadona')).toBeInTheDocument()
      })

      // Add an item
      const input = screen.getByPlaceholderText(/type to search/i)
      await user.type(input, 'Leche')
      await user.click(screen.getByRole('button', { name: /add/i }))

      // Click compare
      const compareButton = screen.getByRole('button', { name: /compare prices/i })
      await user.click(compareButton)

      // Should show comparing state
      expect(screen.getByText(/comparing/i)).toBeInTheDocument()

      await waitFor(() => {
        expect(screen.queryByText(/comparing/i)).not.toBeInTheDocument()
      }, { timeout: 500 })
    })

    it('displays comparison results with best price highlighted', async () => {
      const user = userEvent.setup()
      renderShoppingPage()

      await waitFor(() => {
        expect(screen.getByText('Mercadona')).toBeInTheDocument()
      })

      // Add an item
      const input = screen.getByPlaceholderText(/type to search/i)
      await user.type(input, 'Leche entera')
      await user.click(screen.getByRole('button', { name: /add/i }))

      // Click compare
      const compareButton = screen.getByRole('button', { name: /compare prices/i })
      await user.click(compareButton)

      await waitFor(() => {
        // Should show results section
        expect(screen.getByText(/price comparison/i)).toBeInTheDocument()
        // Should show the trophy/best deal indicator
        expect(screen.getByText('🏆')).toBeInTheDocument()
      })
    })

    it('displays unmatched items warning when items not found', async () => {
      const user = userEvent.setup()

      api.compareBasket.mockResolvedValue({
        ...mockCompareResults,
        unmatched: ['Producto inexistente'],
      })

      renderShoppingPage()

      await waitFor(() => {
        expect(screen.getByText('Mercadona')).toBeInTheDocument()
      })

      // Add an item
      const input = screen.getByPlaceholderText(/type to search/i)
      await user.type(input, 'Producto inexistente')
      await user.click(screen.getByRole('button', { name: /add/i }))
      await user.click(screen.getByRole('button', { name: /compare prices/i }))

      await waitFor(() => {
        expect(screen.getByText(/items not found/i)).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('shows error message when supermarket fetch fails', async () => {
      api.fetchSupermarkets.mockRejectedValue(new Error('Network error'))

      renderShoppingPage()

      await waitFor(() => {
        expect(screen.getByText(/unable to connect/i)).toBeInTheDocument()
      })
    })

    it('shows error message when comparison fails', async () => {
      const user = userEvent.setup()
      api.compareBasket.mockRejectedValue(new Error('Server error'))

      renderShoppingPage()

      await waitFor(() => {
        expect(screen.getByText('Mercadona')).toBeInTheDocument()
      })

      // Add an item and compare
      const input = screen.getByPlaceholderText(/type to search/i)
      await user.type(input, 'Leche')
      await user.click(screen.getByRole('button', { name: /add/i }))
      await user.click(screen.getByRole('button', { name: /compare prices/i }))

      await waitFor(() => {
        expect(screen.getByText(/comparison failed/i)).toBeInTheDocument()
      })
    })
  })
})
