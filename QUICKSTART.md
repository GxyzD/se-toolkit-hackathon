# 🚀 Quick Start Guide - Study Group Matcher V2

## ✅ Current Status

**The project is running successfully locally!**

- **Backend**: Running on http://127.0.0.1:8000
- **Frontend**: Running on http://127.0.0.1:8080 (and also via backend at :8000)
- **Database**: Seeded with 12 students and 3 study groups
- **API Docs**: http://127.0.0.1:8000/docs

## 📍 Access the Application

### Option 1: Via Backend (Recommended)
Open in browser: **http://127.0.0.1:8000/**

### Option 2: Via Frontend Server
Open in browser: **http://127.0.0.1:8080/**

## 🎯 How to Use

### 1. Register a New Student
1. Open the website
2. Fill in the registration form:
   - **Name**: Your full name
   - **Course**: Course code (e.g., CS101, MATH201)
   - **Topics**: Comma-separated topics (e.g., Python,AI,Web)
   - **Availability**: Days and times (e.g., Mon 10-12,Wed 14-16)
   - **Telegram ID** (optional): Get from @userinfobot
3. Click "Register & Find Partners"

### 2. View Your Matches
After registration, you'll see:
- **Dashboard**: Your profile and platform statistics
- **Matches Tab**: Students ranked by compatibility (0-100%)
  - Course match: 50 points
  - Topic overlap: up to 30 points
  - Availability overlap: up to 20 points

### 3. Send Match Requests
1. Go to "Matches" tab
2. Click "Send Match Request" on any student
3. They'll receive a notification (if Telegram configured)

### 4. Accept/Reject Requests
1. Go to "Requests" tab
2. View pending requests
3. Click "Accept" or "Reject"
4. When accepted, a study group is automatically created!

### 5. View Study Groups
1. Go to "Groups" tab
2. See all groups you're a member of
3. View group members and course info

### 6. Browse All Students
1. Go to "Browse Students" tab
2. Search by course code
3. Send match requests to anyone

### 7. AI Assistant
1. Go to "AI Assistant" tab
2. Ask questions about study groups, matching, or study tips
3. Get instant AI-powered responses

## 📊 Pre-loaded Sample Data

The database already contains:

### Students (12 total)
**CS101:**
- Alice Johnson (Python, Algorithms, Data Structures)
- Bob Smith (Python, Web Development, Databases)
- Charlie Brown (Python, Algorithms, Machine Learning)
- Jack Taylor (Python, Databases, Web Development)

**CS201:**
- Diana Prince (Java, OOP, Design Patterns)
- Eve Wilson (Java, Web Development, APIs)
- Karen White (Java, Design Patterns, Testing)

**MATH101:**
- Frank Miller (Calculus, Linear Algebra, Statistics)
- Grace Lee (Calculus, Statistics, Probability)
- Leo Martinez (Linear Algebra, Calculus, Discrete Math)

**CS301:**
- Henry Davis (AI, Neural Networks, Deep Learning)
- Ivy Chen (AI, Machine Learning, Computer Vision)

### Existing Study Groups (3 total)
1. **CS101 Python Study Group** - Alice, Bob, Charlie
2. **CS201 Java Masters** - Diana, Eve, Karen
3. **MATH101 Calculus Circle** - Frank, Grace, Leo

## 🤖 Telegram Bot Setup (Optional)

### 1. Create a Bot
1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the **Bot Token**

### 2. Get Your Chat ID
1. Message [@userinfobot](https://t.me/userinfobot)
2. Copy your **Chat ID**

### 3. Configure the Bot
1. Edit `.env` file:
   ```
   BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   CHAT_ID=123456789
   ```

2. Enable Telegram bot in `backend/app/main.py`:
   Uncomment these lines (around line 47-48):
   ```python
   telegram_thread = threading.Thread(target=start_telegram_bot, daemon=True)
   telegram_thread.start()
   ```

3. Restart the backend:
   ```bash
   # Stop current backend (PID 17308)
   taskkill /F /T /PID 17308
   
   # Restart
   cd backend
   ..\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

### 4. Link Your Telegram Account
1. Register on the website
2. Go to your profile
3. Add your Telegram Chat ID
4. Save

### 5. Use Bot Commands
- `/start` - Link your account
- `/mymatches` - View pending match requests
- `/mygroups` - View your study groups
- `/accept <request_id>` - Accept a match request
- `/reject <request_id>` - Reject a match request
- `/help` - Show all commands

## 🔧 Managing the Application

### Stop the Servers
```bash
# Stop backend
taskkill /F /T /PID 17308

# Stop frontend
taskkill /F /T /PID 23496
```

### Restart the Servers
```bash
# Start backend
cd C:\Users\Gleb\Desktop\software-engineering-toolkit\se-toolkit-hackathon\backend
..\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Start frontend (in new terminal)
cd C:\Users\Gleb\Desktop\software-engineering-toolkit\se-toolkit-hackathon\frontend
python -m http.server 8080
```

### Reset Database
```bash
# Delete the database file
del C:\Users\Gleb\Desktop\software-engineering-toolkit\se-toolkit-hackathon\backend\students.db

# Re-seed
cd C:\Users\Gleb\Desktop\software-engineering-toolkit\se-toolkit-hackathon\backend
..\.venv\Scripts\python -m app.seed
```

## 🌐 Deploy to VM (Production)

When ready to deploy on a VM:

1. **Clone the repository on VM**
2. **Install Docker and Docker Compose**
3. **Update `.env` for production**:
   ```
   DATABASE_URL=postgresql://postgres:postgres@db:5432/study_matcher
   BOT_TOKEN=your_telegram_bot_token
   CHAT_ID=your_chat_id
   ```

4. **Run deployment script**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

   Or manually:
   ```bash
   docker-compose up -d --build
   docker-compose exec backend python -m app.seed
   ```

5. **Setup Telegram webhook** (for production):
   ```bash
   curl -X POST "http://your-vm-ip:8000/api/telegram/setup-webhook?webhook_url=https://your-domain.com/api/telegram/webhook"
   ```

## 📋 API Endpoints

All endpoints are documented at **http://127.0.0.1:8000/docs**

Key endpoints:
- `POST /api/students` - Register student
- `GET /api/students/{id}/matches` - Get matches
- `POST /api/match-requests` - Send request
- `PUT /api/match-requests/{id}/accept` - Accept request
- `GET /api/students/{id}/groups` - Get groups
- `POST /api/ai/ask` - Ask AI

## 🐛 Troubleshooting

**Backend not starting?**
- Check if port 8000 is in use
- Check `.env` file has `DATABASE_URL=sqlite:///./students.db`
- Install dependencies: `pip install -r requirements.txt`

**Matches not showing?**
- Ensure you have students in the database
- Check that courses match (same course = higher score)

**Frontend not loading?**
- Open browser dev tools (F12) and check for errors
- Ensure backend is running (http://127.0.0.1:8000/api/students should work)

**Database errors?**
- Delete `students.db` and re-run seed script
- Check `.env` configuration

## 📞 Need Help?

- Check the full README.md for detailed documentation
- View API docs at http://127.0.0.1:8000/docs
- Use the AI Assistant in the app for questions!

---

**Enjoy finding your perfect study partner! 📚✨**
