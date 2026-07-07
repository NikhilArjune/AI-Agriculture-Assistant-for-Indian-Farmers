<p align="center">
  <img src="https://img.shields.io/badge/🌾-Krishi%20Sahayak-2E7D32?style=for-the-badge&logoColor=white" alt="Krishi Sahayak" />
</p>

<h1 align="center">🌾 AI Agriculture Assistant for Indian Farmers</h1>

<p align="center">
  <strong>Krishi Sahayak — Your AI-Powered Farming Companion</strong><br/>
  A full-stack, LangGraph-powered multi-agent platform designed to solve real problems Indian farmers face daily.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Next.js%2014-000000?style=flat-square&logo=nextdotjs&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/LangGraph-FF6F00?style=flat-square&logo=langchain&logoColor=white" alt="LangGraph" />
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Python%203.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript" />
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Endpoints](#-api-endpoints)
- [Available Make Commands](#-available-make-commands)
- [Multilingual Support](#-multilingual-support)
- [Environment Variables](#-environment-variables)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**Krishi Sahayak** (कृषि सहायक) is more than a chatbot — it's a comprehensive AI-powered platform that helps Indian farmers with:

- 🌱 **Crop Advisory** — What to plant, when to sow, and how to manage crops
- 🦠 **Disease Detection** — Upload a photo and get instant disease diagnosis
- 🌤️ **Weather Alerts** — Real-time weather data and farming-relevant alerts
- 📈 **Market Prices** — Live mandi prices to sell at the right time
- 🏛️ **Government Schemes** — Never miss a subsidy or scheme deadline
- 🧪 **Soil Health** — Soil analysis and fertilizer recommendations
- 💬 **Multilingual Chat** — Converse in Hindi, English, Tamil, Telugu, and more

The platform uses **LangGraph** to orchestrate multiple specialized AI agents. Instead of routing every query through a single generic LLM, a **supervisor agent** classifies the farmer's intent and delegates to the right expert agent — each with its own tools, RAG retrieval, and API integrations.

---

## ✨ Key Features

| Module | Description |
|---|---|
| 🤖 **Multi-Agent AI System** | LangGraph supervisor orchestrates 7+ specialized agents |
| 🔐 **Auth & Profiles** | JWT-based registration, farmer profiles with farm data |
| 🌱 **Crop Advisory** | Region & season-specific planting recommendations |
| 🦠 **Disease Detection** | Image upload → AI-powered disease identification |
| 🌤️ **Weather Service** | OpenWeatherMap integration with farming alerts |
| 📈 **Market Intelligence** | Real-time mandi price tracking |
| 🏛️ **Scheme Finder** | Government scheme discovery & eligibility matching |
| 🧪 **Soil Health** | Soil parameter analysis & fertilizer recommendations |
| 📚 **RAG Knowledge Base** | Qdrant vector DB for agricultural knowledge retrieval |
| 🔔 **Notifications** | Push notifications via Celery background workers |
| 🛡️ **Admin Dashboard** | User management, content moderation, analytics |
| 🌐 **8 Languages** | Hindi, English, Bengali, Tamil, Telugu, Kannada, Marathi, Punjabi |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     NGINX (Reverse Proxy)                │
│                     Port 80 / 443                        │
└──────────┬────────────────────────────────┬──────────────┘
           │                                │
    ┌──────▼──────┐                  ┌──────▼──────┐
    │  Next.js    │                  │  FastAPI    │
    │  Frontend   │   ──REST API──►  │  Backend    │
    │  Port 3000  │                  │  Port 8000  │
    └─────────────┘                  └──────┬──────┘
                                            │
                          ┌─────────────────┼─────────────────┐
                          │                 │                 │
                   ┌──────▼──────┐  ┌───────▼──────┐  ┌──────▼──────┐
                   │  MongoDB    │  │   Redis      │  │   Qdrant    │
                   │  (Users,    │  │  (Cache,     │  │  (Vector    │
                   │   Data)     │  │   Sessions)  │  │   Search)   │
                   └─────────────┘  └──────────────┘  └─────────────┘
```

### LangGraph Multi-Agent Flow

```
Farmer Query ──► Translation Node ──► Supervisor Agent
                                          │
                    ┌─────────┬───────────┼───────────┬─────────┐
                    │         │           │           │         │
                ┌───▼──┐ ┌───▼──┐  ┌─────▼───┐  ┌───▼──┐ ┌───▼───┐
                │ Crop │ │Disease│  │ Weather │  │Market│ │Scheme │
                │Agent │ │Agent │  │  Agent  │  │Agent │ │Agent  │
                └───┬──┘ └───┬──┘  └────┬────┘  └───┬──┘ └───┬───┘
                    │         │          │           │         │
                    └─────────┴──────────┼───────────┴─────────┘
                                         │
                              ┌──────────▼──────────┐
                              │  Validation Node    │
                              │  + Translation      │
                              └──────────┬──────────┘
                                         │
                                    Response ──► Farmer
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | REST API framework |
| **LangGraph** | Multi-agent orchestration |
| **LangChain** | LLM integration layer |
| **Google Gemini** | Primary LLM provider |
| **MongoDB + Beanie** | Document database & ODM |
| **Redis** | Caching, sessions, Celery broker |
| **Qdrant** | Vector database for RAG |
| **Celery** | Background task processing |
| **Sentence Transformers** | Multilingual embeddings |
| **Sentry** | Error tracking & observability |

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 14** | React framework (App Router) |
| **TypeScript** | Type-safe development |
| **TailwindCSS** | Utility-first styling |
| **Zustand** | State management |
| **React Query** | Server state & data fetching |
| **React Hook Form + Zod** | Form handling & validation |
| **next-intl** | Internationalization (8 languages) |
| **Lucide React** | Icon library |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker Compose** | Container orchestration |
| **Nginx** | Reverse proxy, SSL termination |
| **LangSmith** | LLM tracing & debugging |

---

## 📂 Project Structure

```
AI-Agriculture-Assistant-for-Indian-Farmers/
│
├── backend/                    # FastAPI Backend
│   ├── agents/                 # LangGraph agent definitions
│   │   ├── graph.py            # Main LangGraph workflow
│   │   ├── supervisor_agent.py # Intent classifier & router
│   │   ├── crop_agent.py       # Crop advisory agent
│   │   ├── disease_agent.py    # Disease detection agent
│   │   ├── weather_agent.py    # Weather information agent
│   │   ├── market_agent.py     # Market price agent
│   │   ├── scheme_agent.py     # Government schemes agent
│   │   ├── soil_agent.py       # Soil health agent
│   │   ├── rag_agent.py        # RAG knowledge retrieval
│   │   ├── notification_agent.py
│   │   ├── translation_node.py # Language detection & translation
│   │   ├── validation_node.py  # Response quality validation
│   │   └── state.py            # Shared agent state schema
│   ├── routers/                # API route handlers
│   │   ├── auth.py             # Register, login, refresh
│   │   ├── chat.py             # Chat with AI agents
│   │   ├── crops.py            # Crop advisory endpoints
│   │   ├── disease.py          # Disease detection (image upload)
│   │   ├── weather.py          # Weather data endpoints
│   │   ├── market.py           # Market price endpoints
│   │   ├── schemes.py          # Government schemes
│   │   ├── soil.py             # Soil health analysis
│   │   ├── farmers.py          # Farmer profile management
│   │   ├── notifications.py    # Push notifications
│   │   └── admin.py            # Admin dashboard APIs
│   ├── models/                 # MongoDB document models (Beanie)
│   ├── schemas/                # Pydantic request/response schemas
│   ├── tools/                  # Agent tools (API integrations)
│   ├── services/               # Business logic services
│   ├── core/                   # Config, security, logging
│   ├── db/                     # Database connection
│   ├── mcp/                    # Model Context Protocol server
│   ├── workers/                # Celery background tasks
│   ├── scripts/                # Setup & data ingestion scripts
│   ├── tests/                  # Unit & integration tests
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile
│
├── frontend/                   # Next.js 14 Frontend
│   ├── src/
│   │   ├── app/                # App Router pages
│   │   │   ├── dashboard/      # Farmer dashboard
│   │   │   │   ├── chat/       # AI chat interface
│   │   │   │   ├── disease/    # Disease detection page
│   │   │   │   ├── weather/    # Weather dashboard
│   │   │   │   ├── market/     # Market prices page
│   │   │   │   ├── schemes/    # Government schemes
│   │   │   │   ├── soil/       # Soil health page
│   │   │   │   └── profile/    # Farmer profile
│   │   │   ├── admin/          # Admin panel
│   │   │   ├── login/          # Login page
│   │   │   └── register/       # Registration page
│   │   ├── components/         # Shared React components
│   │   ├── lib/                # API client, i18n, utilities
│   │   └── providers/          # React Query provider
│   ├── public/locales/         # Translation files (8 languages)
│   ├── package.json
│   └── Dockerfile
│
├── nginx/                      # Nginx Configuration
│   └── nginx.conf
│
├── docker-compose.yml          # Full-stack container setup
├── Makefile                    # Development shortcuts
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Docker** & **Docker Compose** (recommended)
- **Python 3.11+** (for local backend development)
- **Node.js 18+** & **npm** (for local frontend development)
- API keys: Google Gemini / Groq, OpenWeatherMap

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/NikhilArjune/AI-Agriculture-Assistant-for-Indian-Farmers.git
cd AI-Agriculture-Assistant-for-Indian-Farmers

# 2. Set up environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 3. Start all services
docker compose up -d

# 4. Set up vector database collection
make setup-qdrant

# 5. Seed government schemes data
make seed-schemes
```

The app will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Local Development

#### Backend

```bash
# Create virtual environment
cd backend
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

> **Note**: You'll need MongoDB, Redis, and Qdrant running locally or via Docker. The easiest way is to use Docker Compose for just the databases:
> ```bash
> docker compose up mongodb redis qdrant -d
> ```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| **Auth** | | |
| `POST` | `/api/v1/auth/register` | Register a new farmer |
| `POST` | `/api/v1/auth/login` | Login & get JWT tokens |
| `POST` | `/api/v1/auth/refresh` | Refresh access token |
| **Chat** | | |
| `POST` | `/api/v1/chat` | Send message to AI agents |
| `GET` | `/api/v1/chat/history` | Get conversation history |
| **Crops** | | |
| `GET` | `/api/v1/crops/advisory` | Get crop recommendations |
| **Disease** | | |
| `POST` | `/api/v1/disease/detect` | Upload image for diagnosis |
| **Weather** | | |
| `GET` | `/api/v1/weather` | Get weather data by location |
| `GET` | `/api/v1/weather/alerts` | Get farming weather alerts |
| **Market** | | |
| `GET` | `/api/v1/market/prices` | Get mandi prices |
| **Schemes** | | |
| `GET` | `/api/v1/schemes` | List government schemes |
| **Soil** | | |
| `POST` | `/api/v1/soil/analyze` | Submit soil parameters |
| **Admin** | | |
| `GET` | `/api/v1/admin/users` | List all users (admin only) |
| **Health** | | |
| `GET` | `/health` | Health check endpoint |

Full interactive docs available at `/docs` (Swagger UI) when running in development mode.

---

## ⚡ Available Make Commands

```bash
make up                  # Start all Docker services
make down                # Stop all services
make build               # Rebuild Docker images
make logs                # Tail container logs
make backend-dev         # Run backend locally (no Docker)
make frontend-dev        # Run frontend locally (no Docker)
make setup-qdrant        # Initialize Qdrant vector collection
make seed-schemes        # Load government schemes into DB
make ingest-docs DIR=... TOPIC=...  # Ingest documents into RAG
make worker              # Start Celery worker
make test                # Run unit tests
make test-all            # Run all tests
make lint                # Run linter (ruff)
make lint-fix            # Auto-fix lint issues
```

---

## 🌐 Multilingual Support

The platform supports **8 Indian languages** out of the box:

| Language | Code | Status |
|---|---|---|
| 🇬🇧 English | `en` | ✅ Full |
| 🇮🇳 Hindi | `hi` | ✅ Full |
| 🇮🇳 Bengali | `bn` | ✅ Full |
| 🇮🇳 Tamil | `ta` | ✅ Full |
| 🇮🇳 Telugu | `te` | ✅ Full |
| 🇮🇳 Kannada | `kn` | ✅ Full |
| 🇮🇳 Marathi | `mr` | ✅ Full |
| 🇮🇳 Punjabi | `pa` | ✅ Full |

The **translation node** in the LangGraph pipeline auto-detects the farmer's language and translates responses accordingly using multilingual embeddings (`paraphrase-multilingual-mpnet-base-v2`).

---

## 🔑 Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

| Variable | Description | Required |
|---|---|---|
| `APP_SECRET_KEY` | Application secret for JWT signing | ✅ |
| `MONGO_URI` | MongoDB connection string | ✅ |
| `REDIS_URL` | Redis connection string | ✅ |
| `QDRANT_URL` | Qdrant vector DB URL | ✅ |
| `GOOGLE_API_KEY` | Google Gemini API key | ✅ |
| `GROQ_API_KEY` | Groq API key (alternative LLM) | ⬜ |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | ⬜ |
| `SENTRY_DSN` | Sentry error tracking DSN | ⬜ |
| `LANGCHAIN_API_KEY` | LangSmith tracing key | ⬜ |

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

Please make sure to:
- Follow the existing code style
- Add tests for new features
- Update documentation as needed

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- **LLM_Agri_Bot** — The original chatbot that inspired this full-stack platform
- **LangGraph** by LangChain — For the multi-agent orchestration framework
- **Indian Farmer Community** — For the real-world problems that drive this platform

---

<p align="center">
  Made with ❤️ for Indian Farmers 🇮🇳
</p>
