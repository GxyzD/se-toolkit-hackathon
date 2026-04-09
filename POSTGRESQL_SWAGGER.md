# PostgreSQL & Swagger Setup Guide

## ✅ What Was Implemented

### 1. **PostgreSQL Support** 🐘

**Auto-Detection & Fallback:**
- The app now automatically tries to connect to PostgreSQL first
- If PostgreSQL is unavailable, it gracefully falls back to SQLite
- You'll see a message on startup: 
  - ✅ `Connected to PostgreSQL` (if successful)
  - ⚠️ `PostgreSQL not available, falling back to SQLite` (if not)

**Configuration (`.env`):**
```env
# For PostgreSQL (when Docker/VM is available)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/study_matcher

# For SQLite (local development)
DATABASE_URL=sqlite:///./students.db
```

**PostgreSQL Driver Installed:**
- `psycopg2-binary` added to requirements
- Connection pooling enabled with `pool_pre_ping=True`

**To Use PostgreSQL Locally:**
```bash
# Start PostgreSQL container
docker run -d --name study-matcher-db ^
  -e POSTGRES_USER=postgres ^
  -e POSTGRES_PASSWORD=postgres ^
  -e POSTGRES_DB=study_matcher ^
  -p 5432:5432 postgres:15

# Update .env
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/study_matcher

# Start backend
cd backend
..\..\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

### 2. **Swagger/OpenAPI Documentation** 📚

**Access Points:**
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc  
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

**Features:**
- ✅ Full API documentation with descriptions
- ✅ Organized by tags (Students, Authentication, Matching, Groups, AI Assistant, Statistics, Telegram)
- ✅ Interactive testing - try out endpoints directly from the browser
- ✅ Request/response schemas documented
- ✅ Error responses documented

**API Tags:**
1. **Students** - Registration, profiles, search
2. **Authentication** - Login, change password
3. **Matching** - Find matches, send/accept/reject requests
4. **Groups** - Create and view study groups
5. **AI Assistant** - Ask questions via OpenRouter (Qwen)
6. **Statistics** - Platform metrics
7. **Telegram** - Bot webhook setup

---

## 🚀 How to Start the Server

### Quick Start (SQLite - No Docker Required):
```bash
# Option 1: Use the batch file
start-backend.bat

# Option 2: Manual
cd C:\Users\Gleb\Desktop\software-engineering-toolkit\se-toolkit-hackathon\backend
..\..\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### With PostgreSQL:
```bash
# 1. Start PostgreSQL
docker run -d --name study-matcher-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=study_matcher -p 5432:5432 postgres:15

# 2. Update .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/study_matcher

# 3. Start backend
cd backend
..\..\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

## 📋 What Changed

### Files Modified:
1. **`backend/app/database.py`**
   - Added PostgreSQL auto-detection
   - Graceful fallback to SQLite
   - Connection testing on startup

2. **`backend/app/main.py`**
   - Enhanced FastAPI configuration with full description
   - Added tags to all endpoints for Swagger organization
   - Improved docstrings for all endpoints

3. **`backend/requirements.txt`**
   - Added `psycopg2-binary` for PostgreSQL support

4. **`.env`**
   - Updated to use PostgreSQL URL by default
   - Falls back to SQLite if PostgreSQL unavailable

5. **`docker-compose.yml`**
   - Updated to pass OpenRouter environment variables

6. **`README.md`**
   - Added Swagger documentation section
   - Updated dataset description

---

## 🧪 Testing

### Test Swagger:
1. Start the backend server
2. Open http://127.0.0.1:8000/docs
3. Click on any endpoint to see detailed documentation
4. Click "Try it out" to test endpoints interactively

### Test PostgreSQL:
1. Start PostgreSQL container
2. Update `.env` with PostgreSQL URL
3. Start backend - you should see: `✅ Connected to PostgreSQL`
4. Stop PostgreSQL and restart backend - you'll see fallback to SQLite

---

## 🎯 Current Status

- ✅ PostgreSQL driver installed
- ✅ Database auto-detection implemented
- ✅ Swagger/OpenAPI documentation configured
- ✅ All endpoints tagged and documented
- ✅ Graceful SQLite fallback working
- ⏳ PostgreSQL container not running (Docker not available)

**The app is ready to use with SQLite now, and will automatically use PostgreSQL when you deploy on a VM with Docker!**

---

## 📝 Next Steps for VM Deployment

When deploying to VM with Docker:
1. Docker will start PostgreSQL automatically
2. Update `.env` with PostgreSQL URL
3. Run `docker-compose up -d`
4. App will connect to PostgreSQL automatically
5. Seed database: `docker-compose exec backend python -m app.seed`

Everything is prepared for seamless PostgreSQL + Swagger experience! 🚀
