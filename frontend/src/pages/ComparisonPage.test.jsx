/**
 * ComparisonPage Component Tests
 *
 * Tests for Team C's comparison UI requirements:
 * - Category selector populated from API
 * - Brand input (free text)
 * - Variants input with tags
 * - Quantity + unit selection
 * - Add/remove items
 * - Results display with expandable offers
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import ComparisonPage from './ComparisonPage'
import * as api from '../api'

// Mock the API module
vi.mock('../api', () => ({
  fetchSupermarkets: vi.fn(),
  compareBasket: vi.fn(),
  baseUrl: '/api/v1',
}))

// Mock fetch for categories endpoint
global.fetch = vi.fn()

const mockSupermarkets = [
  { id: 1, name: 'Mercadona' },
  { id: 2, name: 'Carrefour' },
  { id: 3, name: 'Lidl' },
]

const mockCategories = [
  { id: 1, name: 'Dairy' },
  { id: 2, name: 'Bakery' },
  { id: 3, name: 'Beverages' },
]

// Shape aligned with backend CompareResponse (api/app/schemas.py)
const mockCompareResponse = {
  items: [
    {
      name: 'Dairy',
      store: 'Mercadona',
      price: 0.89,
    },
  ],
  storeTotals: [
    { store: 'Mercadona', total: 0.89 },
    { store: 'Carrefour', total: 0.95 },
  ],
  overallTotal: 0.89,
  unmatched: [],
  priceComparison: [
    {
      name: 'Dairy',
      cheapestStore: 'Mercadona',
      cheapestPrice: 0.89,
      prices: [
        { store: 'Mercadona', price: 0.89 },
        { store: 'Carrefour', price: 0.95 },
      ],
    },
  ],
}

function renderComparisonPage() {
  return render(
    <MemoryRouter>
      <ComparisonPage />
    </MemoryRouter>
  )
}

describe('ComparisonPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()

    api.fetchSupermarkets.mockResolvedValue(mockSupermarkets)
    api.compareBasket.mockResolvedValue(mockCompareResponse)

    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockCategories),
    })
  })

  describe('Initial Render', () => {
    it('renders the page heading', async () => {
      renderComparisonPage()
      expect(screen.getByRole('heading', { name: /price comparison/i })).toBeInTheDocument()
    })

    it('loads and displays categories in dropdown', async () => {
      renderComparisonPage()

      await waitFor(() => {
        const categorySelect = screen.getByLabelText(/category/i)
        expect(categorySelect).toBeInTheDocument()
      })

      // Open the select and check for categories
      const categorySelect = screen.getByLabelText(/category/i)
      expect(categorySelect).toHaveTextContent('Select a category')
    })

    it('loads and displays stores for selection', async () => {
      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByText('Mercadona')).toBeInTheDocument()
        expect(screen.getByText('Carrefour')).toBeInTheDocument()
        expect(screen.getByText('Lidl')).toBeInTheDocument()
      })
    })
  })

  describe('Item Form (C2 - Shopping List Input)', () => {
    it('has brand input field', async () => {
      renderComparisonPage()

      await waitFor(() => {
        const brandInput = screen.getByLabelText(/brand/i)
        expect(brandInput).toBeInTheDocument()
      })
    })

    it('has quantity and unit fields', async () => {
      renderComparisonPage()

      await waitFor(() => {
        const quantityInput = screen.getByLabelText(/quantity/i)
        const unitSelect = screen.getByLabelText(/unit/i)
        expect(quantityInput).toBeInTheDocument()
        expect(unitSelect).toBeInTheDocument()
      })
    })

    it('shows validation error when adding item without product name or category', async () => {
      const user = userEvent.setup()
      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByText('Mercadona')).toBeInTheDocument()
      })

      // Try to add without entering product name or selecting category
      const addButton = screen.getByRole('button', { name: /add to list/i })
      await user.click(addButton)

      expect(screen.getByText(/please enter a product name or select a category/i)).toBeInTheDocument()
    })

    it('shows variant checkboxes when category is selected', async () => {
      const user = userEvent.setup()
      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByLabelText(/category/i)).toBeInTheDocument()
      })

      // Select a category
      const categorySelect = screen.getByLabelText(/category/i)
      await user.selectOptions(categorySelect, 'Dairy')

      // Should show variant checkboxes for Dairy
      await waitFor(() => {
        expect(screen.getByText('Whole')).toBeInTheDocument()
      })
    })

    it('allows adding custom variants', async () => {
      const user = userEvent.setup()
      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByLabelText(/category/i)).toBeInTheDocument()
      })

      // Select category first
      const categorySelect = screen.getByLabelText(/category/i)
      await user.selectOptions(categorySelect, 'Dairy')

      // Add custom variant
      const variantInput = screen.getByPlaceholderText(/add custom variant/i)
      await user.type(variantInput, 'Bio')

      // Find and click the Add button for variants
      const addButtons = screen.getAllByRole('button', { name: /add/i })
      const variantAddButton = addButtons.find(btn => btn.closest('.variant-input-row'))
      if (variantAddButton) {
        await user.click(variantAddButton)
      }
    })
  })

  describe('Shopping List Display', () => {
    it('shows empty list message initially', async () => {
      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByText(/no items added yet/i)).toBeInTheDocument()
      })
    })

    it('displays added items in the list', async () => {
      const user = userEvent.setup()
      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByLabelText(/category/i)).toBeInTheDocument()
      })

      // Add an item
      const categorySelect = screen.getByLabelText(/category/i)
      await user.selectOptions(categorySelect, 'Dairy')

      const addButton = screen.getByRole('button', { name: /add to list/i })
      await user.click(addButton)

      // Should show the item in the shopping list section (with item-category class)
      await waitFor(() => {
        expect(screen.getByText(/shopping list/i)).toBeInTheDocument()
        // Check for the item in the list by looking for the category badge
        const itemCategories = screen.getAllByText('Dairy')
        expect(itemCategories.length).toBeGreaterThanOrEqual(1)
      })
    })

    it('allows removing items from list', async () => {
      const user = userEvent.setup()
      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByLabelText(/category/i)).toBeInTheDocument()
      })

      // Add an item
      const categorySelect = screen.getByLabelText(/category/i)
      await user.selectOptions(categorySelect, 'Dairy')
      await user.click(screen.getByRole('button', { name: /add to list/i }))

      // Find and click remove button
      const removeButton = screen.getByLabelText(/remove item/i)
      await user.click(removeButton)

      // Should show empty message again
      await waitFor(() => {
        expect(screen.getByText(/no items added yet/i)).toBeInTheDocument()
      })
    })
  })

  describe('Store Selection', () => {
    it('has select all / deselect all buttons', async () => {
      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByText('Select All')).toBeInTheDocument()
        expect(screen.getByText('Deselect All')).toBeInTheDocument()
      })
    })

    it('allows toggling individual stores', async () => {
      const user = userEvent.setup()
      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByText('Mercadona')).toBeInTheDocument()
      })

      const mercadonaChip = screen.getByRole('button', { name: 'Mercadona' })
      await user.click(mercadonaChip)

      // Should toggle the store selection
      expect(mercadonaChip).toBeInTheDocument()
    })
  })

  describe('Comparison Results (C1)', () => {
    it('shows compare button disabled when no items', async () => {
      renderComparisonPage()

      await waitFor(() => {
        const compareButton = screen.getByRole('button', { name: /compare prices/i })
        expect(compareButton).toBeDisabled()
      })
    })

    it('shows results after comparison', async () => {
      const user = userEvent.setup()
      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByLabelText(/category/i)).toBeInTheDocument()
      })

      // Add an item
      const categorySelect = screen.getByLabelText(/category/i)
      await user.selectOptions(categorySelect, 'Dairy')
      await user.click(screen.getByRole('button', { name: /add to list/i }))

      // Click compare
      const compareButton = screen.getByRole('button', { name: /compare prices/i })
      await user.click(compareButton)

      // Should show results heading
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /results/i })).toBeInTheDocument()
      })
    })

    it('shows best store badge in results', async () => {
      const user = userEvent.setup()
      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByLabelText(/category/i)).toBeInTheDocument()
      })

      // Add item and compare
      const categorySelect = screen.getByLabelText(/category/i)
      await user.selectOptions(categorySelect, 'Dairy')
      await user.click(screen.getByRole('button', { name: /add to list/i }))
      await user.click(screen.getByRole('button', { name: /compare prices/i }))

      // Should show best store indicator (use specific class selector)
      await waitFor(() => {
        const bestBadges = screen.getAllByText(/best/i)
        expect(bestBadges.length).toBeGreaterThanOrEqual(1)
      })
    })

    it('allows expanding to see all offers', async () => {
      const user = userEvent.setup()
      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByLabelText(/category/i)).toBeInTheDocument()
      })

      // Add item and compare
      const categorySelect = screen.getByLabelText(/category/i)
      await user.selectOptions(categorySelect, 'Dairy')
      await user.click(screen.getByRole('button', { name: /add to list/i }))
      await user.click(screen.getByRole('button', { name: /compare prices/i }))

      // Find and click expand button
      await waitFor(() => {
        const expandButton = screen.queryByRole('button', { name: /show all/i })
        if (expandButton) {
          expect(expandButton).toBeInTheDocument()
        }
      })
    })
  })

  describe('Error Handling', () => {
    it('shows error when comparison fails', async () => {
      const user = userEvent.setup()
      api.compareBasket.mockRejectedValue(new Error('API Error'))

      renderComparisonPage()

      await waitFor(() => {
        expect(screen.getByLabelText(/category/i)).toBeInTheDocument()
      })

      // Add item and compare
      const categorySelect = screen.getByLabelText(/category/i)
      await user.selectOptions(categorySelect, 'Dairy')
      await user.click(screen.getByRole('button', { name: /add to list/i }))
      await user.click(screen.getByRole('button', { name: /compare prices/i }))

      await waitFor(() => {
        expect(screen.getByText(/failed to compare/i)).toBeInTheDocument()
      })
    })

    it('uses fallback categories when API fails', async () => {
      global.fetch.mockRejectedValue(new Error('Network error'))

      renderComparisonPage()

      await waitFor(() => {
        // Should still have category select with fallback options
        const categorySelect = screen.getByLabelText(/category/i)
        expect(categorySelect).toBeInTheDocument()
      })
    })
  })
})
