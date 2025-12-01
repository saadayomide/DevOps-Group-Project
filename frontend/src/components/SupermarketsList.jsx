import React from 'react'

export default function SupermarketsList({
  supermarkets = [],
  selected = [],
  setSelected = () => {},
  loading,
  onCompare,
  onResetSelection,
  comparing,
  canCompare = false,
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
        {loading && (
          <div className="loading-placeholder">
            <div className="loading-spinner-small"></div>
            <span className="muted">Loading supermarkets…</span>
          </div>
        )}
        {!loading && (
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
          {supermarkets.length === 0 && <li className="muted">No supermarkets available</li>}
          </ul>
        )}

        <button
          type="button"
          className="btn primary full"
          onClick={onCompare}
          disabled={comparing || !canCompare}
          aria-label="Compare prices across selected supermarkets"
        >
          {comparing ? 'Comparing…' : 'Compare Prices'}
        </button>
        {!canCompare && !comparing && (
          <p className="muted small-text" style={{ marginTop: '-8px', textAlign: 'center' }}>
            {selected.length === 0
              ? 'Select at least one supermarket to compare'
              : 'Add items to your shopping list to compare'}
          </p>
        )}
        <button type="button" className="link muted" onClick={onResetSelection}>
          Reset selection
        </button>
      </div>
    </div>
  )
}
