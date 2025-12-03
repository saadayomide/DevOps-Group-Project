import React, { useEffect, useState } from 'react'
import { fetchSupermarkets } from '../api'
import { useAuth } from '../context/AuthContext'

function Avatar({ name = '' }) {
  const initials = name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((n) => n[0].toUpperCase())
    .join('') || 'SS'

  return <div className="avatar large">{initials}</div>
}

export default function ProfilePage() {
  const { user } = useAuth()
  const [supermarkets, setSupermarkets] = useState([])
  const [selectedDefaults, setSelectedDefaults] = useState([])
  const [currency, setCurrency] = useState('EUR')
  const [showPercent, setShowPercent] = useState(true)
  const [highlightCheapest, setHighlightCheapest] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    setLoading(true)
    fetchSupermarkets()
      .then((list) => {
        setSupermarkets(list)
        setSelectedDefaults(list.slice(0, 2).map((s) => s.name))
      })
      .catch((e) => setError(`Failed to load supermarkets: ${e.message}`))
      .finally(() => setLoading(false))
  }, [])

  const toggleDefault = (name) => {
    setSelectedDefaults((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name],
    )
  }

  const handleSave = (e) => {
    e.preventDefault()
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="profile-page">
      <div className="card profile-card">
        <h2>Profile</h2>
        <div className="profile-info">
          <Avatar name={user?.name} />
          <div>
            <div className="profile-name">{user?.name || 'ShopSmart user'}</div>
            <div className="profile-email">{user?.email || 'you@example.com'}</div>
          </div>
        </div>
        <div className="profile-detail">
          <span className="muted">Email</span>
          <div>{user?.email || 'you@example.com'}</div>
        </div>
      </div>

      <div className="card preferences-card">
        <h2>Preferences</h2>
        {error && <div className="alert error">{error}</div>}
        {loading ? (
          <div className="muted">Loading supermarkets...</div>
        ) : (
          <form className="form" onSubmit={handleSave}>
            <div className="field">
              <span>Default supermarkets</span>
              <div className="chip-group">
                {supermarkets.map((s) => (
                  <button
                    key={s.id ?? s.name}
                    type="button"
                    className={selectedDefaults.includes(s.name) ? 'chip active' : 'chip'}
                    onClick={() => toggleDefault(s.name)}
                  >
                    {s.name}
                  </button>
                ))}
                {!supermarkets.length && <span className="muted">No supermarkets</span>}
              </div>
            </div>

            <div className="field">
              <span>Default currency</span>
              <select value={currency} onChange={(e) => setCurrency(e.target.value)}>
                <option>EUR</option>
                <option>USD</option>
                <option>GBP</option>
              </select>
            </div>

            <div className="field toggle-row">
              <span>Show savings in percentage</span>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={showPercent}
                  onChange={(e) => setShowPercent(e.target.checked)}
                />
                <span className="slider" />
              </label>
            </div>

            <div className="field toggle-row">
              <span>Highlight cheapest supermarket only</span>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={highlightCheapest}
                  onChange={(e) => setHighlightCheapest(e.target.checked)}
                />
                <span className="slider" />
              </label>
            </div>

            {saved && <div className="alert success">Preferences saved</div>}

            <button type="submit" className="btn primary">
              Save changes
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
