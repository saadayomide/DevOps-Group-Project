import React, { useEffect, useState } from 'react'
import { fetchSupermarkets } from '../api'
import { useAuth } from '../context/AuthContext'
import { useShopping } from '../context/ShoppingContext'

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
  const { selectedStores, setStores, clearItems } = useShopping()

  const [supermarkets, setSupermarkets] = useState([])
  const [tempSelectedStores, setTempSelectedStores] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    setLoading(true)
    fetchSupermarkets()
      .then((list) => {
        setSupermarkets(list || [])
        // Initialize temp selection from context
        setTempSelectedStores(selectedStores.length > 0 ? selectedStores : (list || []).slice(0, 2).map((s) => s.name))
      })
      .catch((e) => setError(`Failed to load supermarkets: ${e.message}`))
      .finally(() => setLoading(false))
  }, [selectedStores])

  const toggleDefault = (name) => {
    setTempSelectedStores((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name],
    )
  }

  const handleSave = (e) => {
    e.preventDefault()
    // Save to context (which persists to localStorage)
    setStores(tempSelectedStores)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleClearShoppingList = () => {
    if (window.confirm('Are you sure you want to clear your shopping list?')) {
      clearItems()
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    }
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
              <p className="muted" style={{ fontSize: '0.85rem', marginTop: '0.25rem', marginBottom: '0.5rem' }}>
                Select which supermarkets to compare by default
              </p>
              <div className="chip-group">
                {supermarkets.map((s) => (
                  <button
                    key={s.id ?? s.name}
                    type="button"
                    className={tempSelectedStores.includes(s.name) ? 'chip active' : 'chip'}
                    onClick={() => toggleDefault(s.name)}
                  >
                    {s.name}
                  </button>
                ))}
                {!supermarkets.length && <span className="muted">No supermarkets</span>}
              </div>
            </div>

            <div className="field">
              <span>Shopping list</span>
              <p className="muted" style={{ fontSize: '0.85rem', marginTop: '0.25rem', marginBottom: '0.5rem' }}>
                Your shopping list is automatically saved
              </p>
              <button
                type="button"
                className="btn secondary"
                onClick={handleClearShoppingList}
                style={{ marginTop: '0.5rem' }}
              >
                Clear shopping list
              </button>
            </div>

            {saved && <div className="alert success">Changes saved</div>}

            <button type="submit" className="btn primary">
              Save preferences
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
