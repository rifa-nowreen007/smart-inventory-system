# 📦 SmartInventory-007 — Real Full-Stack App

## 🗄️ Tech Stack
- **Backend:** Python FastAPI + SQLAlchemy + SQLite
- **Auth:** JWT tokens + bcrypt password hashing
- **Frontend:** HTML + JS (connects to real API)
- **Database:** SQLite (file: `smartinventory.db`)

---

## 🚀 How to Run

### Step 1 — Start Backend (REQUIRED FIRST)

```bash
cd SI007/backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
python run.py
```

You will see:
```
╔══════════════════════════════════════════════════════╗
║   📦  SmartInventory-007  API Server                ║
║   API    →  http://localhost:8000                   ║
║   Docs   →  http://localhost:8000/docs              ║
╚══════════════════════════════════════════════════════╝
```

### Step 2 — Start Frontend

```bash
cd SI007/frontend
npm install     # first time only
npm run dev
```

Browser opens → **http://localhost:5173** ✅

---

## 🔐 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| 👑 Admin | admin@stocksmart.io | admin123 |
| 🎯 Manager | manager@stocksmart.io | manager123 |
| 👤 Staff | staff@stocksmart.io | staff123 |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | Login → returns JWT token |
| POST | /api/auth/register | Register new user |
| GET | /api/auth/me | Current user info |
| GET | /api/products | List all products |
| POST | /api/products | Create product (admin) |
| PUT | /api/products/{id} | Update product (admin) |
| DELETE | /api/products/{id} | Delete product (admin) |
| POST | /api/products/{id}/stock | Stock in/out |
| GET | /api/suppliers | List suppliers |
| POST | /api/suppliers | Add supplier |
| GET | /api/orders | List orders |
| POST | /api/orders | Create order |
| GET | /api/transactions | Transaction history |
| GET | /api/users | List users (admin) |
| GET | /api/reports/summary | Dashboard summary |
| GET | /api/reports/inventory/csv | Export CSV |

**Swagger UI:** http://localhost:8000/docs

---

## 📁 Project Structure

```
SI007/
├── backend/
│   ├── run.py              ← Start server: python run.py
│   ├── requirements.txt    ← pip install -r requirements.txt
│   ├── .env                ← Environment variables
│   └── app/
│       ├── main.py         ← FastAPI app + CORS + seed data
│       ├── config.py       ← Settings
│       ├── database.py     ← SQLAlchemy + SQLite
│       ├── models/         ← ORM models (User, Product, etc.)
│       ├── schemas/        ← Pydantic schemas
│       ├── services/       ← JWT + bcrypt auth
│       └── routers/        ← API endpoints
│           ├── auth.py
│           ├── users.py
│           ├── products.py
│           ├── suppliers.py
│           ├── orders.py
│           ├── transactions.py
│           └── reports.py
└── frontend/
    ├── index.html          ← Complete frontend app
    ├── package.json        ← npm run dev
    └── vite.config.js
```
