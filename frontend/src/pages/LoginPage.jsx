import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [remember, setRemember] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isAuthenticated) navigate('/app')
  }, [isAuthenticated, navigate])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!email || !password) {
      setError('Please enter email and password.')
      return
    }
    setError('')
    login(email, password, remember)
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="auth-hero">
          <div className="logo hero-logo">
            <div className="logo-mark">🛒</div>
            <span className="logo-text">ShopSmart</span>
          </div>
          <h1 className="hero-title">
            Compare supermarket prices in real time and save on every trip
          </h1>
          <div className="hero-panels">
            <div className="mini-card">
              <h3>Shopplist</h3>
              <ul className="checklist">
                {['Milk', 'Bread', 'Apples', 'Cheese', 'Pasta'].map((item) => (
                  <li key={item}>
                    <span className="check-icon">✔</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="mini-card">
              <h3>Market</h3>
              <div className="price-row">
                <span>Markutt</span>
                <strong>3,40 €</strong>
              </div>
              <div className="price-row">
                <span>ShopPlus</span>
                <strong>34.5 €</strong>
              </div>
              <div className="badge success">Cheapest basket</div>
            </div>
          </div>
          <ul className="hero-list">
            <li>Add your shopping list in seconds</li>
            <li>Compare prices across supermarkets</li>
            <li>Get the cheapest basket automatically</li>
          </ul>
        </div>

        <div className="auth-panel">
          <h2>Log in</h2>
          <form className="form" onSubmit={handleSubmit}>
            <label className="field">
              <span>Email</span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </label>
            <label className="field">
              <span>Password</span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </label>

            <div className="field horizontal">
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                />
                <span>Remember me</span>
              </label>
              <Link to="#" className="link">
                Forgot password?
              </Link>
            </div>

            {error && <div className="alert error">{error}</div>}

            <button type="submit" className="btn primary full">
              Log in
            </button>
          </form>

          <p className="muted center">
            Don&apos;t have an account?{' '}
            <Link to="/signup" className="link">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
