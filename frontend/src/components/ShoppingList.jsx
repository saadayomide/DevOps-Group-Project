import React, { useState } from 'react'

export default function ShoppingList({ items, setItems }) {
  const [value, setValue] = useState('')

  function addItem() {
    const v = value.trim()
    if (!v) return
    setItems([...items, v])
    setValue('')
  }

  function removeAt(i) {
    setItems(items.filter((_, idx) => idx !== i))
  }

  return (
    <div className="shopping-list">
      <h2>Shopping List</h2>
      <div className="input-row">
        <input
          placeholder="Add item (e.g. milk)"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && addItem()}
        />
        <button onClick={addItem} className="btn">Add</button>
        <button onClick={() => setItems([])} className="btn">Clear</button>
      </div>

      <ul className="items">
        {items.map((it, i) => (
          <li key={`${it}-${i}`}>
            <span>{it}</span>
            <button onClick={() => removeAt(i)} className="small">Remove</button>
          </li>
        ))}
        {!items.length && <li className="muted">No items yet</li>}
      </ul>
    </div>
  )
}
