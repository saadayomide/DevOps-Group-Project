import React from 'react'

export default function Results({ results, comparing, bestStore, savings }) {
  if (!results) {
    return (
      <div className="card results-card">
        <div className="card-header">
          <h2>Results</h2>
        </div>
        <div className="card-body empty-state">
          <div className="empty-icon">🔍</div>
          <h3>Comparison results will appear here</h3>
          <p className="muted">
            Add items to your shopping list and select supermarkets, then click "Compare Prices" to see results.
          </p>
        </div>
      </div>
    )
  }

  const { items = [], storeTotals = [], overallTotal = 0, unmatched = [] } = results

  return (
    <div className="card results-card">
      <div className="card-header">
        <h2>Comparison Results</h2>
        {comparing && <span className="badge">Updating…</span>}
      </div>

      <div className="card-body">
        <div className="results-summary">
          <div className="summary-main">
            <span className="muted">Best Option</span>
            <div className="summary-value">
              {bestStore ? (
                <>
                  <strong>{bestStore.store}</strong> – Total: €{Number(bestStore.total).toFixed(2)}
                </>
              ) : (
                `Overall total: €${Number(overallTotal).toFixed(2)}`
              )}
            </div>
          </div>
          {savings !== null && savings !== undefined && savings > 0 && (
            <div className="summary-save">
              <span className="muted">You save up to</span>
              <div className="savings">€{savings.toFixed(2)}</div>
            </div>
          )}
        </div>

        <div className="store-totals">
          <h3 className="section-title">Store Totals</h3>
          {storeTotals.map((t) => (
            <div
              key={t.store}
              className={
                bestStore && bestStore.store === t.store
                  ? 'store-card active'
                  : 'store-card'
              }
            >
              <span className="store-name">{t.store}</span>
              <span className="store-total">€{Number(t.total).toFixed(2)}</span>
            </div>
          ))}
          {!storeTotals.length && <div className="muted">No totals available</div>}
        </div>

        <div className="results-divider"></div>

        <div className="table-section">
          <h3 className="section-title">Item Details</h3>
          <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th>Cheapest Store</th>
                <th>Price</th>
              </tr>
            </thead>
            <tbody>
              {items.map((it, i) => {
                const price =
                  typeof it.price === 'number' ? it.price.toFixed(2) : it.price
                return (
                  <tr key={`${it.name}-${i}`}>
                    <td>{it.name}</td>
                    <td>{it.store || 'N/A'}</td>
                    <td className="price-cell">
                      <span className="price-value">€{price}</span>
                    </td>
                  </tr>
                )
              })}
              {!items.length && (
                <tr>
                  <td colSpan="3" className="muted" style={{ textAlign: 'center', padding: '20px' }}>
                    No matched items found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          </div>
        </div>

        {unmatched && unmatched.length > 0 && (
          <div className="unmatched">
            <h4>Items not found</h4>
            <ul>
              {unmatched.map((u) => (
                <li key={u}>{u}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
