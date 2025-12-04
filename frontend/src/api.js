export const baseUrl = import.meta.env.VITE_API_BASE || '/api/v1'

async function request(path, options = {}) {
  const res = await fetch(`${baseUrl}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${text}`)
  }
  return res.json()
}

export function fetchSupermarkets() {
  return request('/supermarkets/')
}

export function compareBasket(items, stores) {
  return request('/compare/', {
    method: 'POST',
    body: JSON.stringify({ items, stores }),
  })
}

// Search products for autocomplete
export function searchProducts(query, limit = 10) {
  if (!query || query.length < 2) return Promise.resolve([])
  return request(`/products/?q=${encodeURIComponent(query)}&limit=${limit}`)
}
