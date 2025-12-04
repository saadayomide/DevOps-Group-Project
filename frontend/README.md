# ShopSmart Frontend

React/Vite frontend for the ShopSmart price comparison application.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Visit `http://localhost:5173` to use the app.

## Environment Variables

Create a `.env.local` file with:

```
VITE_API_BASE=http://localhost:8000/api/v1
```

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Create production build |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

## Project Structure

```
src/
├── pages/           # Page components
│   ├── LoginPage.jsx
│   ├── SignupPage.jsx
│   ├── ShoppingPage.jsx
│   └── ProfilePage.jsx
├── context/         # React contexts
│   ├── AuthContext.jsx
│   └── ShoppingContext.jsx
├── layouts/         # Layout components
│   └── PageLayout.jsx
├── api.js           # API client functions
├── App.jsx          # Main app with routing
├── main.jsx         # Entry point
└── index.css        # Global styles
```

## Features

- **User Authentication**: Login and signup flows
- **Shopping List**: Add items with autocomplete suggestions
- **Store Selection**: Choose which supermarkets to compare
- **Price Comparison**: View prices across stores with best deal highlighting
- **Persistent State**: Shopping list saves across navigation and browser sessions

## Backend Requirements

The frontend expects these API endpoints:

- `GET /api/v1/supermarkets/` - List supermarkets
- `GET /api/v1/products/?q=<query>` - Search products
- `POST /api/v1/compare/` - Compare prices

See the `api/` folder for backend setup.
