import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function SignupPage() {
  const { signup, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (isAuthenticated) navigate('/app')
  }, [isAuthenticated, navigate])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!name || !email || !password || !confirm) {
      setError('Please complete all fields.')
      return
    }
    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }
    setError('')
    signup(name, email, password)
  }

  return (
    <div className="auth-shell">
      <div className="signup-card">
        <div className="signup-left">
          <div className="logo hero-logo">
            <div className="logo-mark">🛒</div>
            <span className="logo-text">ShopSmart</span>
          </div>
          <h1>Sign up</h1>
          <p className="muted">Create your account to start comparing prices in seconds.</p>
          <form className="form" onSubmit={handleSubmit}>
            <label className="field">
              <span>Name</span>
              <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" />
            </label>
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
            <label className="field">
              <span>Confirm password</span>
              <input
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                placeholder="••••••••"
              />
            </label>

            {error && <div className="alert error">{error}</div>}

            <button type="submit" className="btn primary full">
              Sign up
            </button>
          </form>
          <p className="muted">
            Already have an account?{' '}
            <Link to="/" className="link">
              Log in
            </Link>
          </p>
        </div>

        <div className="signup-illustration">
          <div className="mini-card illustration-card">
            <div className="illustration-avatar">😊</div>
            <p className="illustration-text">Save money by comparing prices across supermarkets</p>
          </div>
        </div>
      </div>
    </div>
  )
}
