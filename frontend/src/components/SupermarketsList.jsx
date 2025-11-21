import React from 'react'

export default function SupermarketsList({ supermarkets = [], selected = [], setSelected = () => {}, loading }) {
  function toggle(name) {
    if (selected.includes(name)) setSelected(selected.filter((s) => s !== name))
    else setSelected([...selected, name])
  }

  return (
    <div className="supermarkets">
      <h2>Supermarkets</h2>
      {loading && <div className="muted">Loading supermarkets…</div>}
      <ul className="stores">
        {supermarkets.map((s) => (
          <li key={s.id ?? s.name}>
            <label>
              <input
                type="checkbox"
                checked={selected.includes(s.name)}
                onChange={() => toggle(s.name)}
              />
              {s.name}
            </label>
          </li>
        ))}
        {!loading && supermarkets.length === 0 && <li className="muted">No supermarkets</li>}
      </ul>
    </div>
  )
}
