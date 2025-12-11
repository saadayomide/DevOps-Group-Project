import { vi } from 'vitest'

// Mock supermarkets data
export const mockSupermarkets = [
  { id: 1, name: 'Mercadona' },
  { id: 2, name: 'Carrefour' },
  { id: 3, name: 'Lidl' },
]

// Mock products for search
export const mockProducts = [
  { id: 1, name: 'Leche entera' },
  { id: 2, name: 'Leche desnatada' },
  { id: 3, name: 'Pan integral' },
]

// Mock comparison results
export const mockCompareResults = {
  items: [
    { name: 'Leche entera', store: 'Mercadona', price: 0.89 },
    { name: 'Pan integral', store: 'Lidl', price: 1.20 },
  ],
  storeTotals: [
    { store: 'Mercadona', total: 2.09 },
    { store: 'Carrefour', total: 2.35 },
    { store: 'Lidl', total: 2.15 },
  ],
  priceComparison: [
    {
      name: 'Leche entera',
      cheapestStore: 'Mercadona',
      prices: [
        { store: 'Mercadona', price: 0.89 },
        { store: 'Carrefour', price: 0.95 },
        { store: 'Lidl', price: 0.92 },
      ],
    },
    {
      name: 'Pan integral',
      cheapestStore: 'Lidl',
      prices: [
        { store: 'Mercadona', price: 1.25 },
        { store: 'Carrefour', price: 1.30 },
        { store: 'Lidl', price: 1.20 },
      ],
    },
  ],
  overallTotal: 2.09,
  unmatched: [],
}

// Mock categories
export const mockCategories = [
  { id: 1, name: 'Dairy' },
  { id: 2, name: 'Bakery' },
  { id: 3, name: 'Meat & Poultry' },
  { id: 4, name: 'Fruits & Vegetables' },
  { id: 5, name: 'Beverages' },
]

// Create mock API functions
export const createMockApi = () => ({
  fetchSupermarkets: vi.fn().mockResolvedValue(mockSupermarkets),
  searchProducts: vi.fn().mockResolvedValue(mockProducts),
  compareBasket: vi.fn().mockResolvedValue(mockCompareResults),
})

// Mock fetch responses helper
export const mockFetchResponse = (data, ok = true, status = 200) => {
  return Promise.resolve({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
  })
}
