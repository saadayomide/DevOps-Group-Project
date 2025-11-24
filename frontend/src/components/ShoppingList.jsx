import React, { useState } from 'react'

export default function ShoppingList({ items, setItems }) {
  const [value, setValue] = useState('')

  const addItem = () => {
    const trimmed = value.trim()
    if (!trimmed) return
    setItems([...items, trimmed])
    setValue('')
  }

  const removeAt = (index) => {
    setItems(items.filter((_, i) => i !== index))
  }

  const clearList = () => setItems([])

  return (
    <div className="card shopping-card">
      <div className="card-header">
        <h2>Shopping List</h2>
      </div>

      <div className="card-body">
        <div className="stacked-input">
          <input
            placeholder="Add an item (e.g. 1L milk, eggs, pasta...)"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addItem()}
          />
          <button type="button" onClick={addItem} className="btn primary full">
            Add
          </button>
        </div>
        <button type="button" className="link muted" onClick={clearList}>
          Clear list
        </button>

        <ul className="item-list">
          {items.map((it, i) => (
            <li key={`${it}-${i}`}>
              <span>{it}</span>
              <button type="button" className="icon-button" onClick={() => removeAt(i)}>
                ×
              </button>
            </li>
          ))}
          {!items.length && <li className="muted">No items yet</li>}
        </ul>
      </div>
    </div>
  )
}
