import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function Logo() {
  return (
    <div className="logo">
      <div className="logo-mark">🛒</div>
      <span className="logo-text">ShopSmart</span>
    </div>
  )
}

function Avatar({ name = '' }) {
  const initials = name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((n) => n[0].toUpperCase())
    .join('') || 'SS'

  return <div className="avatar">{initials}</div>
}

export default function PageLayout({ children }) {
  const { user, logout } = useAuth()

  return (
    <div className="app-shell">
      <header className="topbar">
        <Logo />

        <nav className="nav-links">
          <NavLink
            to="/app"
            className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
          >
            Shopping
          </NavLink>
          <NavLink
            to="/comparison"
            className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
          >
            Compare Prices
          </NavLink>
          <NavLink
            to="/profile"
            className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
          >
            Profile
          </NavLink>
        </nav>

        <div className="nav-user">
          <Avatar name={user?.name} />
          <div className="nav-user-info">
            <span className="nav-user-name">Hi, {user?.name || 'Guest'}</span>
            <button type="button" className="link-button" onClick={logout}>
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="page-content">{children}</main>
    </div>
  )
}
