<<<<<<< HEAD
# Study Group Matcher

A smart matching platform that connects university students based on courses, topics, and availability to form effective study groups.

## Product Context

### Demo
![Family Shopping List Screenshot1](https://github.com/GxyzD/se-toolkit-hackathon/blob/341468b6361c2bb44599e4c46642ad893e8fa51b/assets/screenshots/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-04-11%20002324.png)
![Family Shopping List Screenshot2](https://github.com/GxyzD/se-toolkit-hackathon/blob/341468b6361c2bb44599e4c46642ad893e8fa51b/assets/screenshots/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-04-11%20002411.png)
![Family Shopping List Screenshot3](https://github.com/GxyzD/se-toolkit-hackathon/blob/341468b6361c2bb44599e4c46642ad893e8fa51b/assets/screenshots/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-04-11%20002550.png)

### End Users

University students (undergraduate and graduate) who are looking for study partners to collaborate with on coursework, exam preparation, and group projects.

### Problem

Students struggle to find peers with matching courses, schedules, and academic interests for effective group study. This leads to:
- Inefficient solo studying
- Missed opportunities for collaborative learning
- Difficulty coordinating schedules with potential study partners
- No centralized platform to find and connect with study partners

### Solution

Study Group Matcher is an intelligent web platform that automatically connects students based on:
- **Course enrollment** - Same or related courses
- **Topic interests** - Overlapping subjects and skills
- **Schedule availability** - Common free time slots

The platform uses a smart scoring algorithm (0-100 points) to rank compatibility and facilitates study group formation through a request-accept system with Telegram notifications.

## Features

### ✅ Implemented Features

- **Secure Authentication** - Password-protected accounts with SHA-256 hashing and unique usernames
- **Smart Matching Algorithm** - Compatibility scoring based on:
  - Course match: 50 points (same course) or 25 points (same department)
  - Topic overlap: 0-30 points (Jaccard similarity)
  - Availability overlap: 0-20 points (common days and time slots)
- **Match Request System** - Send, accept, or reject match requests
- **Automatic Study Groups** - Groups form when both students accept a match
- **AI Assistant** - Powered by Qwen via OpenRouter for study tips and platform help
- **Interactive Dashboard** - View stats, profile, matches, requests, and groups
- **Student Browsing** - Search and filter students by course
- **Swagger/OpenAPI Documentation** - Full interactive API docs at `/docs`
- **Database Support** - PostgreSQL for production, SQLite for development with auto-fallback
- **Docker Deployment** - Ready for local development and VM production deployment
- **Sample Dataset** - 12 pre-configured students across 4 courses with 3 study groups

### 🚧 Not Yet Implemented

- Real-time in-app messaging/chat between group members
- Calendar integration for scheduling
- Video call scheduling and integration
- File sharing within study groups
- Advanced matching preferences and filters
- Study session history and tracking
- Mobile application (iOS/Android)
- Multi-language support

## Usage

### Quick Start (Local Development)

1. **Prerequisites:**
   - Python 3.11+ or Docker & Docker Compose
   - Modern web browser

2. **Clone and navigate to project:**
   ```bash
   cd se-toolkit-hackathon
   ```

3. **Configure environment:**
   Edit `.env` file with your settings:
   ```env
   # OpenRouter AI (for AI assistant)
   OPENROUTER_API_KEY=sk-or-v1-your-api-key
   OPENROUTER_MODEL=qwen/qwen-2.5-72b-instruct

   # Telegram (optional)
   BOT_TOKEN=your_telegram_bot_token
   CHAT_ID=your_chat_id

   # Database (SQLite for local, PostgreSQL for production)
   DATABASE_URL=sqlite:///./students.db
   ```

4. **Start the application:**

   **Option A: Using Python (no Docker required)**
   ```bash
   # Install dependencies
   cd backend
   pip install -r requirements.txt

   # Seed database with sample data
   python -m app.seed

   # Start backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

   **Option B: Using Docker**
   ```bash
   docker-compose up --build
   ```

5. **Access the application:**
   - Frontend: http://127.0.0.1:8000/
   - API Documentation (Swagger): http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

6. **Register and explore:**
   - Click "Register" to create an account
   - Or login with pre-loaded accounts (password: `student123`):
     - Alice Johnson, Bob Smith, Charlie Brown (CS101)
     - Diana Prince, Eve Wilson, Karen White (CS201)
     - Frank Miller, Grace Lee, Leo Martinez (MATH101)

### How to Use the Platform

1. **Register** with your name, course, topics, and availability
2. **View Matches** - See students ranked by compatibility (0-100%)
3. **Send Request** - Click "Send Match Request" to potential partners
4. **Accept/Reject** - Respond to incoming requests in "Requests" tab
5. **Form Groups** - When accepted, a study group is automatically created
6. **Get Notifications** - Configure Telegram for real-time updates
7. **Ask AI** - Use AI Assistant for study tips and platform help

## Deployment

### Target Environment

- **Operating System:** Ubuntu 24.04 LTS (same as university VMs)
- **Architecture:** x86_64 (64-bit)

### VM Requirements

The following should be installed on the VM:

- **Docker** (v24.0+) and **Docker Compose** (v2.0+)
- **Git** for cloning the repository
- **Nginx** (optional, for reverse proxy and HTTPS)
- **OpenSSL** (optional, for SSL certificates)
- Minimum 2 GB RAM, 10 GB disk space

### Step-by-Step Deployment Instructions

#### Step 1: Connect to Your VM

```bash
ssh username@your-vm-ip
```

#### Step 2: Install Docker and Docker Compose

```bash
# Update package list
sudo apt update

# Install prerequisites
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, avoids using sudo)
sudo usermod -aG docker $USER
```

Verify installation:
```bash
docker --version
docker compose version
```

#### Step 3: Clone the Repository

```bash
cd ~
git clone <your-repository-url>
cd se-toolkit-hackathon
```

#### Step 4: Configure Environment Variables

Create and edit the `.env` file:

```bash
nano .env
```

Add the following configuration:

```env
# Telegram Bot (create via @BotFather on Telegram)
BOT_TOKEN=your_telegram_bot_token_here
CHAT_ID=your_chat_id_here

# OpenRouter AI (get key from https://openrouter.ai/)
OPENROUTER_API_KEY=sk-or-v1-your-api-key
OPENROUTER_MODEL=qwen/qwen-2.5-72b-instruct

# Database (PostgreSQL for production)
DATABASE_URL=postgresql://postgres:postgres@db:5432/study_matcher
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X` in nano).

#### Step 5: Start Services

```bash
# Build and start containers in detached mode
docker compose up -d --build
```

This will start:
- **Backend** (FastAPI on port 8000)
- **Frontend** (served by backend)
- **PostgreSQL** database (port 5432, internal only)

#### Step 6: Seed the Database

```bash
# Populate database with sample data
docker compose exec backend python -m app.seed
```

You should see:
```
✓ Created 12 students
✓ Created 3 study groups
Database seeding completed!
```

#### Step 7: Configure Telegram Webhook (Optional)

If you configured a Telegram bot, set up the webhook:

```bash
curl -X POST "http://localhost:8000/api/telegram/setup-webhook?webhook_url=https://your-domain.com/api/telegram/webhook"
```

#### Step 8: Verify Deployment

Check if services are running:

```bash
# View running containers
docker compose ps

# Check backend logs
docker compose logs backend

# Test API
curl http://localhost:8000/api/stats
```

Expected response:
```json
{"total_students":12,"total_groups":3,"pending_requests":0}
```

#### Step 9: Setup Reverse Proxy (Optional, for HTTPS)

If you have a domain name, install and configure Nginx:

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/study-matcher
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/study-matcher /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Step 10: Setup SSL (Optional, Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Access Your Deployed Application

After deployment, your application will be available at:

- **Production URL:** http://your-vm-ip:8000/ or https://your-domain.com
- **API Docs:** http://your-vm-ip:8000/docs

### Managing the Application

```bash
# View logs
docker compose logs -f

# Restart services
docker compose restart

# Stop all services
docker compose down

# Update and redeploy
git pull
docker compose up -d --build

# Backup database
docker compose exec db pg_dump -U postgres study_matcher > backup.sql

# Restore database
cat backup.sql | docker compose exec -T db psql -U postgres study_matcher
```

### Troubleshooting

**Backend not starting:**
```bash
docker compose logs backend
docker compose down && docker compose up -d --build
```

**Database connection issues:**
```bash
# Check PostgreSQL is running
docker compose ps db

# Restart database
docker compose restart db
```

**Telegram bot not working:**
- Verify BOT_TOKEN and CHAT_ID in `.env`
- Check logs: `docker compose logs backend | grep Telegram`

**Port already in use:**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

## Project Structure

```
se-toolkit-hackathon/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app with all endpoints
│   │   ├── models.py               # SQLAlchemy database models
│   │   ├── schemas.py              # Pydantic validation schemas
│   │   ├── database.py             # Database configuration (PostgreSQL/SQLite)
│   │   ├── matching.py             # Smart matching algorithm
│   │   ├── ai_agent.py             # AI assistant (OpenRouter/Qwen)
│   │   ├── bot.py                  # Telegram bot functions
│   │   ├── telegram_handler.py     # Telegram command processor
│   │   └── seed.py                 # Database seed script
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile                  # Backend Docker image
├── frontend/
│   ├── index.html                  # Main web interface
│   ├── style.css                   # Styling
│   ├── script.js                   # Frontend JavaScript
│   └── Dockerfile                  # Frontend Docker image
├── .env                            # Environment variables
├── docker-compose.yml              # Docker orchestration
└── README.md                       # This file
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

All endpoints are organized by tags: Students, Authentication, Matching, Groups, AI Assistant, Statistics, and Telegram.

## License

MIT License

## Contributing

Contributions are welcome! Please open issues and submit pull requests for any improvements or bug fixes.
=======
# se-toolkit-hackathon
123
>>>>>>> e4304e79a316704918c269c10c4ee8cf65105c1d
