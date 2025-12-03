import React, { useState } from 'react'

export default function ShoppingList({ items, setItems }) {
  const [value, setValue] = useState('')
  const [error, setError] = useState('')

  const addItem = () => {
    const trimmed = value.trim()

    // Validation: No empty items
    if (!trimmed) {
      setError('Please enter an item name')
      return
    }

    // Validation: No duplicates (case-insensitive)
    const normalized = trimmed.toLowerCase()
    if (items.some(item => item.toLowerCase() === normalized)) {
      setError('This item is already in your list')
      return
    }

    setError('')
    setItems([...items, trimmed])
    setValue('')
  }

  const removeAt = (index) => {
    setItems(items.filter((_, i) => i !== index))
    setError('')
  }

  const clearList = () => {
    setItems([])
    setError('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      addItem()
    }
  }

  return (
    <div className="card shopping-card">
      <div className="card-header">
        <h2>Shopping List</h2>
        <p className="muted small-text">Add items you want to compare</p>
      </div>

      <div className="card-body">
        <div className="field">
          <label htmlFor="item-input" className="field-label">
            Item Name
          </label>
          <div className="stacked-input">
            <input
              id="item-input"
              type="text"
              placeholder="e.g., Milk, Bread, Eggs, Pasta..."
              value={value}
              onChange={(e) => {
                setValue(e.target.value)
                setError('')
              }}
              onKeyDown={handleKeyDown}
              aria-label="Add item to shopping list"
            />
            <button type="button" onClick={addItem} className="btn primary full">
              Add Item
            </button>
          </div>
          {error && (
            <div className="alert error" role="alert">
              <span className="error-icon">⚠️</span>
              <span className="error-text">{error}</span>
            </div>
          )}
        </div>

        {items.length > 0 && (
          <button type="button" className="link muted" onClick={clearList}>
            Clear all items
          </button>
        )}

        <div className="item-list-container">
          <h3 className="item-list-title">Your Items ({items.length})</h3>
          <ul className="item-list">
            {items.map((it, i) => (
              <li key={`${it}-${i}`}>
                <span>{it}</span>
                <button
                  type="button"
                  className="icon-button"
                  onClick={() => removeAt(i)}
                  aria-label={`Remove ${it}`}
                >
                  ×
                </button>
              </li>
            ))}
            {!items.length && (
              <li className="muted empty-item">
                No items yet. Add items above to start comparing prices.
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  )
}
