<div align="center">
  <img src="frontend/public/logo.svg" width="120" height="120" alt="LifeHub Logo"/>
  <h1 align="center" style="margin-top: 0.5rem; font-size: 2.5rem;">LifeHub</h1>
  <p align="center" style="font-size: 1.1rem; color: #666;">
    Your unified personal life management system
  </p>
</div>

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react" alt="React"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"/>
</p>

---

## ✨ Overview

**LifeHub** is a full-stack personal life management application that brings together projects, tasks, notes, finances, calendar events, reading lists, and an AI-powered assistant — all in one place.

Built with a modern tech stack and designed with dark mode and internationalization (EN/PT-BR) from day one.

---

## 🚀 Features

### 📋 Projects & Tasks
- Full CRUD with soft delete
- Priority levels (low → urgent)
- Status tracking (active, paused, completed, archived)
- Progress bar with percentage
- Categories for organization
- Start and target dates
- External links per project

### 📝 Notes
- Markdown content with live preview
- Pin important notes to top
- Tag system for filtering
- Soft delete with restore

### 💰 Finances
- Income/expense tracking
- Monthly summaries with balance
- Category-based budget limits
- Visual progress bars for budgets

### 📅 Calendar
- Interactive monthly calendar grid
- Day selection with event filtering
- All-day and timed events
- Description support
- Event CRUD with inline editing

### 📚 Readings
- Track books, articles, videos, links, and ideas
- Status: unread → reading → completed → archived
- Priority rating system

### 🤖 AI Assistant
- Powered by OpenCode Zen (free tier)
- Natural language commands for all modules
- Streaming responses with Markdown rendering
- Session-based conversation history
- Tool calling system (create tasks, add transactions, etc.)

### 🎨 Design
- Dark mode with system preference detection
- Internationalization (English / Português BR)
- Responsive sidebar layout
- Tailwind CSS styling

---

## 🏗 Tech Stack

| Layer       | Technology                                      |
|-------------|-------------------------------------------------|
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy (async), Pydantic |
| **Frontend**| React 19, TypeScript 5, Vite 6, Tailwind CSS 3, Zustand 5 |
| **Database**| PostgreSQL 16                                   |
| **AI**      | OpenCode Zen API (multi-provider architecture)  |

---

## 📁 Project Structure

```
lifehub/
├── backend/
│   ├── app/
│   │   ├── core/           # Auth, base models, exceptions
│   │   ├── modules/        # Feature modules
│   │   │   ├── ai/         # AI chat, providers, tools
│   │   │   ├── calendar/   # Events
│   │   │   ├── finances/   # Transactions, budgets
│   │   │   ├── notes/      # Notes with markdown
│   │   │   ├── projects/   # Projects & tasks
│   │   │   └── readings/   # Reading list
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── api/            # HTTP client
│   │   ├── modules/        # Stores (auth, theme, i18n), UI components
│   │   ├── pages/          # Route pages
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── start.sh
└── README.md
```

---

## 🔧 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 16
- `npm` or `yarn`

### 1. Clone & Install

```bash
git clone https://github.com/DevFalconszz/lifehub.git
cd lifehub
```

#### Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

### 2. Configure

Copy the environment template:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your database credentials:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/lifehub
SECRET_KEY=your-secret-key
```

### 3. Run

```bash
./start.sh
```

Or separately:

```bash
# Terminal 1 — backend
cd backend && python3 run.py

# Terminal 2 — frontend
cd frontend && npx vite --host
```

Open [http://localhost:5173](http://localhost:5173) and register your account.

---

## 🧪 API Overview

| Method | Endpoint                    | Description        |
|--------|-----------------------------|--------------------|
| POST   | `/api/auth/register`        | Create account     |
| POST   | `/api/auth/login`           | Sign in            |
| GET    | `/api/auth/me`              | Current user       |
| GET    | `/api/projects`             | List projects      |
| POST   | `/api/projects`             | Create project     |
| PATCH  | `/api/projects/{id}`        | Update project     |
| DELETE | `/api/projects/{id}`        | Delete project     |
| GET    | `/api/tasks`                | List tasks         |
| POST   | `/api/tasks`                | Create task        |
| ...    | *(similar for all modules)* |                    |

Full API docs at [http://localhost:8004/docs](http://localhost:8004/docs) (Swagger UI).

---

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/DevFalconszz">DevFalconszz</a>
</p>
