import React from 'react'

export default function Results({ results }) {
  if (!results) {
    return <div className="muted">No results yet. Click Compare.</div>
  }

  const { items = [], storeTotals = [], overallTotal = 0, unmatched = [] } = results

  return (
    <div className="results">
      <h2>Results</h2>

      <div className="section">
        <h3>Items</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Item</th>
              <th>Store</th>
              <th>Price</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it, i) => (
              <tr key={`${it.name}-${i}`}>
                <td>{it.name}</td>
                <td>{it.store}</td>
                <td className="price">{typeof it.price === 'number' ? it.price.toFixed(2) : it.price}</td>
              </tr>
            ))}
            {!items.length && (
              <tr>
                <td colSpan="3" className="muted">No matched items</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="section">
        <h3>Store totals</h3>
        <ul>
          {storeTotals.map((t) => (
            <li key={t.store}>
              <strong>{t.store}</strong>: ${Number(t.total).toFixed(2)}
            </li>
          ))}
        </ul>
        <div className="overall">Best overall total: <strong>${Number(overallTotal).toFixed(2)}</strong></div>
      </div>

      {unmatched && unmatched.length > 0 && (
        <div className="section">
          <h3>Unmatched items</h3>
          <ul>
            {unmatched.map((u) => <li key={u} className="muted">{u}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}
