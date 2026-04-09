"""
Telegram Bot Handler - Processes incoming updates from Telegram Bot API.
This runs as a separate thread or can be triggered via webhook.
"""
import os
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def handle_telegram_update(update: dict, db: Session):
    """Handle incoming Telegram update."""
    if "message" not in update:
        return {"ok": True}
    
    message = update["message"]
    chat_id = str(message["chat"]["id"])
    text = message.get("text", "")
    
    # Process commands
    if text.startswith("/start"):
        return handle_start_command(chat_id, db)
    elif text.startswith("/mymatches"):
        return handle_mymatches_command(chat_id, db)
    elif text.startswith("/mygroups"):
        return handle_mygroups_command(chat_id, db)
    elif text.startswith("/accept"):
        return handle_accept_command(chat_id, text, db)
    elif text.startswith("/reject"):
        return handle_reject_command(chat_id, text, db)
    elif text.startswith("/help"):
        return handle_help_command(chat_id)
    else:
        return {"ok": True}

def send_message(chat_id: str, text: str):
    """Send message to telegram."""
    if not BOT_TOKEN:
        print("Telegram not configured")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram send error: {e}")

def handle_start_command(chat_id: str, db):
    """Handle /start command - link telegram account."""
    from . import models
    
    # Check if student with this telegram_id exists
    student = db.query(models.Student).filter(models.Student.telegram_id == chat_id).first()
    
    if student:
        send_message(chat_id, f"✅ Welcome back, {student.name}!\n\nYou're already registered for course {student.course}.\n\nUse /mymatches to see pending requests or /mygroups to see your groups.")
    else:
        send_message(chat_id, f"👋 Welcome to Study Group Matcher!\n\nTo link your Telegram account:\n1. Go to the website\n2. Register or login\n3. Enter your Telegram Chat ID in your profile\n\nYou can get your Chat ID by messaging @userinfobot on Telegram.\n\nUse /help to see available commands.")
    
    return {"ok": True}

def handle_mymatches_command(chat_id: str, db):
    """Handle /mymatches command - show pending requests."""
    from . import models
    
    student = db.query(models.Student).filter(models.Student.telegram_id == chat_id).first()
    
    if not student:
        send_message(chat_id, "❌ You're not linked to any account. Please register on the website first and add your Telegram Chat ID.")
        return {"ok": True}
    
    # Get pending requests
    requests_list = db.query(models.MatchRequest).filter(
        models.MatchRequest.to_student_id == student.id,
        models.MatchRequest.status == "pending"
    ).all()
    
    if not requests_list:
        send_message(chat_id, f"✅ {student.name}, you have no pending match requests.")
        return {"ok": True}
    
    message = f"📨 <b>Pending Match Requests ({len(requests_list)})</b>\n\n"
    for req in requests_list:
        from_student = req.from_student
        message += f"👤 <b>{from_student.name}</b>\n"
        message += f"   Course: {from_student.course}\n"
        if from_student.topics:
            message += f"   Topics: {from_student.topics}\n"
        message += f"   Request ID: {req.id}\n"
        message += f"   Use /accept {req.id} to accept\n"
        message += f"   Use /reject {req.id} to reject\n\n"
    
    send_message(chat_id, message)
    return {"ok": True}

def handle_mygroups_command(chat_id: str, db):
    """Handle /mygroups command - show user's groups."""
    from . import models
    
    student = db.query(models.Student).filter(models.Student.telegram_id == chat_id).first()
    
    if not student:
        send_message(chat_id, "❌ You're not linked to any account. Please register on the website first.")
        return {"ok": True}
    
    # Get groups
    groups = db.query(models.Group).join(models.GroupMember).filter(
        models.GroupMember.student_id == student.id
    ).all()
    
    if not groups:
        send_message(chat_id, f"📚 {student.name}, you're not in any study groups yet. Accept a match to form a group!")
        return {"ok": True}
    
    message = f"👥 <b>Your Study Groups ({len(groups)})</b>\n\n"
    for group in groups:
        members = db.query(models.GroupMember).filter(models.GroupMember.group_id == group.id).all()
        member_names = [db.query(models.Student).filter(models.Student.id == m.student_id).first().name for m in members]
        
        message += f"📚 <b>{group.name}</b>\n"
        message += f"   Course: {group.course}\n"
        message += f"   Members: {', '.join(member_names)}\n\n"
    
    send_message(chat_id, message)
    return {"ok": True}

def handle_accept_command(chat_id: str, text: str, db):
    """Handle /accept command - accept a match request."""
    from . import models
    
    student = db.query(models.Student).filter(models.Student.telegram_id == chat_id).first()
    
    if not student:
        send_message(chat_id, "❌ You're not linked to any account.")
        return {"ok": True}
    
    # Extract request ID
    parts = text.split()
    if len(parts) < 2:
        send_message(chat_id, "❌ Usage: /accept <request_id>\nUse /mymatches to see pending requests.")
        return {"ok": True}
    
    try:
        request_id = int(parts[1])
    except ValueError:
        send_message(chat_id, "❌ Invalid request ID. Use /mymatches to see valid IDs.")
        return {"ok": True}
    
    # Find and accept request
    match_request = db.query(models.MatchRequest).filter(
        models.MatchRequest.id == request_id,
        models.MatchRequest.to_student_id == student.id,
        models.MatchRequest.status == "pending"
    ).first()
    
    if not match_request:
        send_message(chat_id, "❌ Request not found or already processed.")
        return {"ok": True}
    
    match_request.status = "accepted"
    db.commit()
    
    # Update stats
    from_student = match_request.from_student
    to_student = match_request.to_student
    from_student.matches_accepted = (from_student.matches_accepted or 0) + 1
    to_student.matches_accepted = (to_student.matches_accepted or 0) + 1
    db.commit()
    
    # Create group
    from . import matching
    group = matching.create_group_from_match(db, request_id)
    
    if group:
        send_message(chat_id, f"✅ You accepted {from_student.name}'s match request!\n\n🎉 Study group created: {group.name}\n\nCheck the website for details!")
        
        # Notify other student
        if from_student.telegram_id:
            send_message(
                from_student.telegram_id,
                f"✅ {to_student.name} accepted your match request!\n\n🎉 Study group created: {group.name}"
            )
    
    return {"ok": True}

def handle_reject_command(chat_id: str, text: str, db):
    """Handle /reject command - reject a match request."""
    from . import models
    
    student = db.query(models.Student).filter(models.Student.telegram_id == chat_id).first()
    
    if not student:
        send_message(chat_id, "❌ You're not linked to any account.")
        return {"ok": True}
    
    # Extract request ID
    parts = text.split()
    if len(parts) < 2:
        send_message(chat_id, "❌ Usage: /reject <request_id>\nUse /mymatches to see pending requests.")
        return {"ok": True}
    
    try:
        request_id = int(parts[1])
    except ValueError:
        send_message(chat_id, "❌ Invalid request ID.")
        return {"ok": True}
    
    # Find and reject request
    match_request = db.query(models.MatchRequest).filter(
        models.MatchRequest.id == request_id,
        models.MatchRequest.to_student_id == student.id,
        models.MatchRequest.status == "pending"
    ).first()
    
    if not match_request:
        send_message(chat_id, "❌ Request not found or already processed.")
        return {"ok": True}
    
    match_request.status = "rejected"
    db.commit()
    
    send_message(chat_id, f"❌ You rejected {match_request.from_student.name}'s match request.")
    
    # Notify other student
    from_student = match_request.from_student
    if from_student.telegram_id:
        send_message(
            from_student.telegram_id,
            f"❌ {student.name} rejected your match request."
        )
    
    return {"ok": True}

def handle_help_command(chat_id: str):
    """Handle /help command."""
    help_text = """
🤖 <b>Study Group Matcher Bot</b>

<b>Available Commands:</b>

/start - Link your Telegram account
/mymatches - View pending match requests
/mygroups - View your study groups
/accept &lt;id&gt; - Accept a match request
/reject &lt;id&gt; - Reject a match request
/help - Show this help message

<b>How to use:</b>
1. Register on the website
2. Add your Telegram Chat ID in your profile
3. Use bot commands to manage matches

<b>Getting your Chat ID:</b>
Message @userinfobot on Telegram to get your ID.
"""
    send_message(chat_id, help_text)
    return {"ok": True}

def poll_telegram_updates(db):
    """Poll Telegram for updates (for development, use webhook for production)."""
    if not BOT_TOKEN:
        print("Telegram bot not configured")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    offset = 0
    
    print("Starting Telegram bot polling...")
    
    import time
    while True:
        try:
            params = {"offset": offset, "timeout": 30}
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                updates = response.json().get("result", [])
                for update in updates:
                    handle_telegram_update(update, db)
                    offset = update["update_id"] + 1
            else:
                print(f"Telegram polling error: {response.status_code}")
                
        except Exception as e:
            print(f"Telegram polling exception: {e}")
        
        time.sleep(1)
