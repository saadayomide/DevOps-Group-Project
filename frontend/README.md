**Frontend — Run & Develop**

This document explains how to run the frontend locally and how to connect it to the backend. Follow the steps below from the repository root; no machine-specific paths are required.

**Prerequisites**
- **Node**: Install Node.js (LTS recommended, e.g. Node 18+).
- **Package manager**: `npm` is used in commands below (use `npm ci` for CI/reproducible installs).
- **Backend**: The backend must be running and reachable (see the `api` module README).

**Quick start (development)**
- **Install dependencies:**

```powershell
cd frontend
npm ci
```

- **Create local env file:**
- Create a file named `.env.local` in the `frontend/` folder with one line pointing to your running API. Example:

```text
VITE_API_BASE=http://localhost:8000/api/v1
```

- **Start dev server (interactive):**

```powershell
npm run dev
```

- Vite will print the local URL (commonly `http://localhost:5173`) — open that in the browser.

**Build / Preview (production-like)**
- **Create a production build:**

```powershell
npm run build
```

- **Preview the production build locally:**

```powershell
npm run preview
```

**Backend requirements**
- The frontend expects the backend API to serve endpoints under the base path you configure in `VITE_API_BASE` (the example above is `http://localhost:8000/api/v1`).
- To start the backend for local testing (from repository root):

```powershell
cd api
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Troubleshooting**
- **Wrong API base / 404s:** Verify `.env.local` `VITE_API_BASE` matches the backend URL and path prefix.
- **Port in use:** Vite defaults to `5173` and backend to `8000`. Change ports by passing `--port` to `npm run dev` or the `uvicorn` command.
- **Node modules issues:** If you see dependency errors, try removing `node_modules` and `package-lock.json`, then run `npm ci` again.
- **NPM audit warnings:** Run `npm audit` and `npm audit fix` if you want to attempt automatic fixes (may update packages).

**Collaboration / CI notes**
- For CI, prefer `npm ci` to ensure reproducible installs.
- Keep `VITE_API_BASE` configurable via environment files for different environments (dev/staging/prod).

If you'd like, I can also add a short `Makefile` or PowerShell script to unify common tasks (`dev`, `build`, `preview`).
# ShopSmart Frontend (Team A)

This folder contains a minimal Vite + React frontend scaffold for the ShopSmart UI.

Quick start:

```bash
cd frontend
npm install
npm run dev
```

Environment:
- Set `VITE_API_BASE` in `.env.local` to the backend base path (default: `/api/v1`).

Notes for Team B:
- Backend endpoints expected: `GET /api/v1/supermarkets/` and `POST /api/v1/compare`.
- Ensure CORS and base URL configuration when integrating.
