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
          <h3>No comparison yet</h3>
          <p className="muted">
            Add items and select supermarkets to find the best price.
          </p>
        </div>
      </div>
    )
  }

  const { items = [], storeTotals = [], overallTotal = 0, unmatched = [] } = results

  return (
    <div className="card results-card">
      <div className="card-header">
        <h2>Results</h2>
        {comparing && <span className="badge">Updating…</span>}
      </div>

      <div className="card-body">
        <div className="results-summary">
          <div className="summary-main">
            <span className="muted">Best option</span>
            <div className="summary-value">
              {bestStore ? (
                <>
                  {bestStore.store} – Total: €{Number(bestStore.total).toFixed(2)}
                </>
              ) : (
                `Overall total: €${Number(overallTotal).toFixed(2)}`
              )}
            </div>
          </div>
          {savings !== null && savings !== undefined && (
            <div className="summary-save">
              <span className="muted">You save up to</span>
              <div className="savings">€{savings.toFixed(2)}</div>
            </div>
          )}
        </div>

        <div className="store-totals">
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

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th>Best store</th>
                <th>Price</th>
                <th>Other stores / notes</th>
              </tr>
            </thead>
            <tbody>
              {items.map((it, i) => {
                const price =
                  typeof it.price === 'number' ? it.price.toFixed(2) : it.price
                const notes =
                  it.notes ||
                  it.alternatives?.map((a) => `${a.store}: €${a.price}`).join(', ')
                return (
                  <tr key={`${it.name}-${i}`}>
                    <td>{it.name}</td>
                    <td>{it.store}</td>
                    <td className="price-cell">
                      <span className="price-value">€{price}</span>
                    </td>
                    <td className="muted">{notes || '—'}</td>
                  </tr>
                )
              })}
              {!items.length && (
                <tr>
                  <td colSpan="4" className="muted">
                    No matched items
                  </td>
                </tr>
              )}
            </tbody>
          </table>
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
