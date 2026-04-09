from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from typing import List
import os
import threading
import hashlib
import secrets

from .database import get_db, engine, SessionLocal
from . import models, schemas, matching, ai_agent, bot, telegram_handler

def hash_password(password: str) -> str:
    """Hash password with salt using SHA-256."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash."""
    try:
        salt, hashed = stored_hash.split('$')
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except (ValueError, AttributeError):
        return False

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Study Group Matcher API",
    description="""
## 📚 Study Group Matcher - Version 2

A smart matching system that connects university students based on course, topics, and availability.

### Features
- **Student Registration** - Full profiles with authentication
- **Smart Matching** - AI-powered compatibility scoring (0-100)
- **Match Requests** - Send, accept, reject match requests
- **Study Groups** - Automatic group formation
- **AI Assistant** - Chat with Qwen AI via OpenRouter
- **Telegram Bot** - Notifications and commands

### Authentication
All students register with a unique name and password. Passwords are securely hashed with SHA-256 + salt.

### Matching Algorithm
- **Course Match**: 50 points (same course) or 25 points (same department)
- **Topic Overlap**: 0-30 points (Jaccard similarity)
- **Availability Overlap**: 0-20 points (common days and times)

### Sample Accounts
All pre-loaded students use password: `student123`
""",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Study Group Matcher Support",
        "url": "http://localhost:8000",
    },
    license_info={
        "name": "MIT License",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Start Telegram bot polling in background
def start_telegram_bot():
    """Start Telegram bot polling in a separate thread."""
    db = SessionLocal()
    try:
        bot.setup_bot_commands()
        telegram_handler.poll_telegram_updates(db)
    except Exception as e:
        print(f"Telegram bot error: {e}")
    finally:
        db.close()

# Uncomment to enable Telegram bot polling (runs in background)
# telegram_thread = threading.Thread(target=start_telegram_bot, daemon=True)
# telegram_thread.start()

# ============ STUDENT ENDPOINTS ============

@app.post("/api/students", response_model=schemas.StudentResponse, tags=["Students"])
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """
    Register a new student with password.
    
    - **name**: Unique username (cannot be duplicated)
    - **password**: At least 6 characters
    - **course**: Course code (e.g., CS101)
    - **topics**: Comma-separated topics list
    - **availability**: Comma-separated time slots
    - **telegram_id**: Optional Telegram chat ID
    """
    # Check if student with this name already exists
    existing = db.query(models.Student).filter(models.Student.name == student.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student with this name already exists. Please login instead.")
    
    # Hash password
    password_hash = hash_password(student.password)
    
    # Create student with hashed password
    student_data = student.model_dump()
    student_data['password_hash'] = password_hash
    del student_data['password']
    
    db_student = models.Student(**student_data)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    # Check for existing matches
    matches = matching.find_matches(db, db_student.id)
    if matches:
        bot.send_telegram_message(
            f"🎉 New student registered: {db_student.name}\n"
            f"Course: {db_student.course}\n"
            f"Found {len(matches)} potential match(es)!"
        )

    return db_student

@app.post("/api/auth/login", response_model=schemas.LoginResponse, tags=["Authentication"])
def login(credentials: schemas.StudentLogin, db: Session = Depends(get_db)):
    """
    Login with name and password.
    
    Returns success status and student data if credentials are valid.
    """
    student = db.query(models.Student).filter(models.Student.name == credentials.name).first()

    if not student:
        return schemas.LoginResponse(
            success=False,
            message="Student not found. Please register first."
        )

    # Verify password
    if not verify_password(credentials.password, student.password_hash):
        return schemas.LoginResponse(
            success=False,
            message="Incorrect password. Please try again."
        )

    return schemas.LoginResponse(
        success=True,
        message="Login successful!",
        student=student
    )

@app.post("/api/auth/change-password", tags=["Authentication"])
def change_password(student_id: int, old_password: str, new_password: str, db: Session = Depends(get_db)):
    """
    Change password for a student.
    
    - **student_id**: Student ID
    - **old_password**: Current password
    - **new_password**: New password (min 6 chars)
    """
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Verify old password
    if not verify_password(old_password, student.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    
    # Hash new password
    student.password_hash = hash_password(new_password)
    
    db.commit()
    return {"success": True, "message": "Password changed successfully"}

@app.get("/api/students", response_model=List[schemas.StudentResponse], tags=["Students"])
def list_students(db: Session = Depends(get_db)):
    """Get all students."""
    return db.query(models.Student).all()

@app.get("/api/students/{student_id}", response_model=schemas.StudentResponse, tags=["Students"])
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get student by ID."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get("/api/students/search", tags=["Students"])
def search_students(course: str = None, db: Session = Depends(get_db)):
    """Search students by course."""
    query = db.query(models.Student)
    if course:
        query = query.filter(models.Student.course.ilike(f"%{course}%"))
    return query.all()

# ============ MATCHING ENDPOINTS ============

@app.get("/api/students/{student_id}/matches", tags=["Matching"])
def get_matches(student_id: int, db: Session = Depends(get_db)):
    """
    Get best matches for a student.
    
    Returns students ranked by compatibility score (0-100).
    """
    matches = matching.find_matches(db, student_id)
    return [{
        "id": m["student"].id,
        "name": m["student"].name,
        "course": m["student"].course,
        "topics": m["student"].topics,
        "availability": m["student"].availability,
        "score": m["score"],
        "common_topics": m.get("common_topics", ""),
        "common_availability": m.get("common_availability", "")
    } for m in matches]

@app.get("/api/students/{student_id}/requests", response_model=List[schemas.MatchRequestResponse], tags=["Matching"])
def get_requests(student_id: int, db: Session = Depends(get_db)):
    """Get pending match requests for a student."""
    requests = db.query(models.MatchRequest).filter(
        models.MatchRequest.to_student_id == student_id,
        models.MatchRequest.status == "pending"
    ).all()
    return requests

@app.post("/api/match-requests", response_model=schemas.MatchRequestResponse, tags=["Matching"])
def create_match_request(request: schemas.MatchRequestCreate, student_id: int, db: Session = Depends(get_db)):
    """Send a match request to another student."""
    existing = db.query(models.MatchRequest).filter(
        models.MatchRequest.from_student_id == student_id,
        models.MatchRequest.to_student_id == request.to_student_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Request already sent")

    db_request = models.MatchRequest(
        from_student_id=student_id,
        to_student_id=request.to_student_id
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # Notify via Telegram
    from_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    to_student = db.query(models.Student).filter(models.Student.id == request.to_student_id).first()

    bot.send_telegram_message(
        f"📨 New match request from {from_student.name} to {to_student.name}!\n"
        f"Check the website to accept or reject."
    )

    return db_request

@app.put("/api/match-requests/{request_id}/{action}", tags=["Matching"])
def respond_to_request(request_id: int, action: str, db: Session = Depends(get_db)):
    """Accept or reject a match request."""
    match_request = db.query(models.MatchRequest).filter(models.MatchRequest.id == request_id).first()
    if not match_request:
        raise HTTPException(status_code=404, detail="Request not found")

    if action not in ["accept", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    match_request.status = "accepted" if action == "accept" else "rejected"
    db.commit()

    if action == "accept":
        # Update student stats
        from_student = match_request.from_student
        to_student = match_request.to_student
        from_student.matches_accepted = (from_student.matches_accepted or 0) + 1
        to_student.matches_accepted = (to_student.matches_accepted or 0) + 1
        db.commit()
        
        group = matching.create_group_from_match(db, request_id)
        if group:
            bot.send_telegram_message(
                f"🎉 Study group formed!\n"
                f"Group: {group.name}\n"
                f"Members: {from_student.name} & {to_student.name}\n"
                f"Check the website for details."
            )
            
            # Send Telegram notification to both students if they have telegram_id
            if from_student.telegram_id:
                bot.send_telegram_message_direct(
                    from_student.telegram_id,
                    f"✅ {to_student.name} accepted your match request!\n"
                    f"Study group created: {group.name}"
                )
            if to_student.telegram_id:
                bot.send_telegram_message_direct(
                    to_student.telegram_id,
                    f"✅ You accepted {from_student.name}'s match request!\n"
                    f"Study group created: {group.name}"
                )

    return {"status": "success", "action": action}

# ============ GROUP ENDPOINTS ============

@app.post("/api/groups", response_model=schemas.GroupResponse, tags=["Groups"])
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    """Create a study group."""
    db_group = models.Group(name=group.name, course=group.course)
    db.add(db_group)
    db.flush()

    for student_id in group.student_ids:
        member = models.GroupMember(group_id=db_group.id, student_id=student_id)
        db.add(member)
        # Update student stats
        student = db.query(models.Student).filter(models.Student.id == student_id).first()
        if student:
            student.groups_joined = (student.groups_joined or 0) + 1

    db.commit()
    db.refresh(db_group)
    return db_group

@app.get("/api/groups", response_model=List[schemas.GroupResponse], tags=["Groups"])
def list_groups(db: Session = Depends(get_db)):
    """Get all groups."""
    return db.query(models.Group).options(
        joinedload(models.Group.members).joinedload(models.GroupMember.student)
    ).all()

@app.get("/api/students/{student_id}/groups", tags=["Groups"])
def get_student_groups(student_id: int, db: Session = Depends(get_db)):
    """Get all groups for a specific student."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    groups = db.query(models.Group).options(
        joinedload(models.Group.members).joinedload(models.GroupMember.student)
    ).join(models.GroupMember).filter(
        models.GroupMember.student_id == student_id
    ).all()
    
    # Convert to schema format
    result = []
    for group in groups:
        members = [member.student for member in group.members if member.student]
        result.append({
            "id": group.id,
            "name": group.name,
            "course": group.course,
            "members": members,
            "created_at": group.created_at
        })
    
    return result

@app.get("/api/groups/{group_id}", response_model=schemas.GroupResponse, tags=["Groups"])
def get_group(group_id: int, db: Session = Depends(get_db)):
    """Get group details."""
    group = db.query(models.Group).options(
        joinedload(models.Group.members).joinedload(models.GroupMember.student)
    ).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

# ============ AI AGENT ENDPOINT ============

@app.post("/api/ai/ask", response_model=schemas.AIResponse, tags=["AI Assistant"])
def ask_ai(question: schemas.AIQuestion, db: Session = Depends(get_db)):
    """Ask the AI agent a question."""
    student_count = db.query(models.Student).count()
    group_count = db.query(models.Group).count()
    context = f"Platform stats: {student_count} students registered, {group_count} study groups formed."

    answer = ai_agent.ask_ai_agent(question.question, context)
    return schemas.AIResponse(answer=answer)

# ============ STATISTICS ENDPOINT ============

@app.get("/api/stats", tags=["Statistics"])
def get_stats(db: Session = Depends(get_db)):
    """Get platform statistics."""
    student_count = db.query(models.Student).count()
    group_count = db.query(models.Group).count()
    pending_requests = db.query(models.MatchRequest).filter(
        models.MatchRequest.status == "pending"
    ).count()
    
    return {
        "total_students": student_count,
        "total_groups": group_count,
        "pending_requests": pending_requests
    }

# ============ TELEGRAM WEBHOOK ============

@app.post("/api/telegram/webhook", tags=["Telegram"])
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """Receive Telegram webhook updates."""
    update = await request.json()
    return telegram_handler.handle_telegram_update(update, db)

@app.post("/api/telegram/setup-webhook", tags=["Telegram"])
async def setup_webhook(webhook_url: str = None):
    """Setup Telegram webhook URL."""
    if not bot.BOT_TOKEN:
        raise HTTPException(status_code=400, detail="Telegram bot not configured")
    
    url = f"https://api.telegram.org/bot{bot.BOT_TOKEN}/setWebhook"
    if webhook_url is None:
        # Use default based on request
        webhook_url = "https://your-domain.com/api/telegram/webhook"
    
    payload = {"url": webhook_url}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return {"status": "success", "response": response.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to setup webhook: {str(e)}")

# ============ WEB INTERFACE ============

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    """Serve the main HTML page."""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "index.html")
    with open(frontend_path, "r", encoding="utf-8") as f:
        return f.read()
