import React from 'react'

export default function SupermarketsList({
  supermarkets = [],
  selected = [],
  setSelected = () => {},
  loading,
  onCompare,
  onResetSelection,
  comparing,
}) {
  const toggle = (name) => {
    if (selected.includes(name)) setSelected(selected.filter((s) => s !== name))
    else setSelected([...selected, name])
  }

  return (
    <div className="card supermarkets-card">
      <div className="card-header">
        <h2>Supermarkets</h2>
        <p className="muted small-text">Choose where you want to compare</p>
      </div>
      <div className="card-body">
        {loading && <div className="muted">Loading supermarkets…</div>}
        <ul className="stores checklist">
          {supermarkets.map((s) => (
            <li key={s.id ?? s.name}>
              <label>
                <input
                  type="checkbox"
                  checked={selected.includes(s.name)}
                  onChange={() => toggle(s.name)}
                />
                <span>{s.name}</span>
              </label>
            </li>
          ))}
          {!loading && supermarkets.length === 0 && <li className="muted">No supermarkets</li>}
        </ul>

        <button
          type="button"
          className="btn primary full"
          onClick={onCompare}
          disabled={comparing}
        >
          {comparing ? 'Comparing…' : 'Compare prices'}
        </button>
        <button type="button" className="link muted" onClick={onResetSelection}>
          Reset selection
        </button>
      </div>
    </div>
  )
}
