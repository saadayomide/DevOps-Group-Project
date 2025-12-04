import React, { createContext, useContext, useState, useEffect, useMemo } from 'react'

const STORAGE_KEY = 'shopsmart:shopping'
const ShoppingContext = createContext()

export function ShoppingProvider({ children }) {
  // Initialize state from localStorage
  const [items, setItems] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        return parsed.items || []
      } catch {
        return []
      }
    }
    return []
  })

  const [selectedStores, setSelectedStores] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        return parsed.selectedStores || []
      } catch {
        return []
      }
    }
    return []
  })

  const [results, setResults] = useState(null)

  // Persist to localStorage whenever items or selectedStores change
  useEffect(() => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ items, selectedStores })
    )
  }, [items, selectedStores])

  const addItem = (item) => {
    if (item && !items.some((i) => i.toLowerCase() === item.toLowerCase())) {
      setItems((prev) => [...prev, item])
    }
  }

  const removeItem = (item) => {
    setItems((prev) => prev.filter((i) => i !== item))
  }

  const clearItems = () => {
    setItems([])
  }

  const toggleStore = (name) => {
    setSelectedStores((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name]
    )
  }

  const setStores = (stores) => {
    setSelectedStores(stores)
  }

  const value = useMemo(
    () => ({
      items,
      selectedStores,
      results,
      addItem,
      removeItem,
      clearItems,
      toggleStore,
      setStores,
      setResults,
    }),
    [items, selectedStores, results]
  )

  return <ShoppingContext.Provider value={value}>{children}</ShoppingContext.Provider>
}

export function useShopping() {
  const context = useContext(ShoppingContext)
  if (!context) {
    throw new Error('useShopping must be used within a ShoppingProvider')
  }
  return context
}
