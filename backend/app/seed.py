"""
Seed script to populate database with sample student data.
Run this after the application starts for the first time.
Usage: python -m app.seed
"""
import sys
import os
import hashlib
import secrets

# Add parent directory to path for direct execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

# Create tables
models.Base.metadata.create_all(bind=engine)

def hash_password(password: str) -> str:
    """Hash password with salt using SHA-256."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def seed_database(db: Session):
    """Populate database with sample student data."""
    
    # Check if data already exists
    existing_count = db.query(models.Student).count()
    if existing_count > 0:
        print(f"Database already has {existing_count} students. Skipping seed.")
        return
    
    print("Seeding database with sample data...")
    
    # Sample students dataset (all with password 'student123')
    common_password = "student123"
    password_hash = hash_password(common_password)
    
    students_data = [
        {
            "name": "Alice Johnson",
            "password_hash": password_hash,
            "course": "CS101",
            "topics": "Python,Algorithms,Data Structures",
            "availability": "Mon 10-12,Wed 14-16,Fri 10-12",
            "telegram_id": None,
            "matches_accepted": 0,
            "groups_joined": 1
        },
        {
            "name": "Bob Smith",
            "password_hash": password_hash,
            "course": "CS101",
            "topics": "Python,Web Development,Databases",
            "availability": "Mon 10-12,Tue 14-16,Thu 10-12",
            "telegram_id": None,
            "matches_accepted": 0,
            "groups_joined": 1
        },
        {
            "name": "Charlie Brown",
            "password_hash": password_hash,
            "course": "CS101",
            "topics": "Python,Algorithms,Machine Learning",
            "availability": "Wed 14-16,Thu 14-16,Fri 10-12",
            "telegram_id": None,
            "matches_accepted": 0,
            "groups_joined": 1
        },
        {
            "name": "Diana Prince",
            "password_hash": password_hash,
            "course": "CS201",
            "topics": "Java,OOP,Design Patterns",
            "availability": "Mon 14-16,Wed 10-12,Fri 14-16",
            "telegram_id": None,
            "matches_accepted": 0,
            "groups_joined": 1
        },
        {
            "name": "Eve Wilson",
            "password_hash": password_hash,
            "course": "CS201",
            "topics": "Java,Web Development,APIs",
            "availability": "Tue 10-12,Wed 10-12,Thu 14-16",
            "telegram_id": None,
            "matches_accepted": 0,
            "groups_joined": 1
        },
        {
            "name": "Frank Miller",
            "password_hash": password_hash,
            "course": "MATH101",
            "topics": "Calculus,Linear Algebra,Statistics",
            "availability": "Mon 10-12,Tue 10-12,Wed 14-16",
            "telegram_id": None,
            "matches_accepted": 0,
            "groups_joined": 1
        },
        {
            "name": "Grace Lee",
            "password_hash": password_hash,
            "course": "MATH101",
            "topics": "Calculus,Statistics,Probability",
            "availability": "Mon 10-12,Thu 10-12,Fri 14-16",
            "telegram_id": None,
            "matches_accepted": 0,
            "groups_joined": 1
        },
        {
            "name": "Henry Davis",
            "password_hash": password_hash,
            "course": "CS301",
            "topics": "AI,Neural Networks,Deep Learning",
            "availability": "Tue 14-16,Wed 14-16,Fri 10-12",
            "telegram_id": None,
            "matches_accepted": 0,
            "groups_joined": 0
        },
        {
            "name": "Ivy Chen",
            "password_hash": password_hash,
            "course": "CS301",
            "topics": "AI,Machine Learning,Computer Vision",
            "availability": "Mon 14-16,Tue 14-16,Thu 10-12",
            "telegram_id": None,
            "matches_accepted": 0,
            "groups_joined": 0
        },
        {
            "name": "Jack Taylor",
            "password_hash": password_hash,
            "course": "CS101",
            "topics": "Python,Databases,Web Development",
            "availability": "Mon 10-12,Wed 14-16,Thu 14-16",
            "telegram_id": None,
            "matches_accepted": 0,
            "groups_joined": 0
        },
        {
            "name": "Karen White",
            "password_hash": password_hash,
            "course": "CS201",
            "topics": "Java,Design Patterns,Testing",
            "availability": "Mon 14-16,Wed 10-12,Fri 14-16",
            "telegram_id": None,
            "matches_accepted": 0,
            "groups_joined": 1
        },
        {
            "name": "Leo Martinez",
            "password_hash": password_hash,
            "course": "MATH101",
            "topics": "Linear Algebra,Calculus,Discrete Math",
            "availability": "Tue 10-12,Wed 14-16,Fri 10-12",
            "telegram_id": None,
            "matches_accepted": 0,
            "groups_joined": 1
        }
    ]
    
    # Create students
    students = []
    for student_data in students_data:
        student = models.Student(**student_data)
        db.add(student)
        students.append(student)
    
    db.commit()
    
    # Create some initial groups for demonstration
    groups_data = [
        {
            "name": "CS101 Python Study Group",
            "course": "CS101",
            "member_ids": [1, 2, 3]  # Alice, Bob, Charlie
        },
        {
            "name": "CS201 Java Masters",
            "course": "CS201",
            "member_ids": [4, 5, 11]  # Diana, Eve, Karen
        },
        {
            "name": "MATH101 Calculus Circle",
            "course": "MATH101",
            "member_ids": [6, 7, 12]  # Frank, Grace, Leo
        }
    ]
    
    for group_data in groups_data:
        group = models.Group(
            name=group_data["name"],
            course=group_data["course"]
        )
        db.add(group)
        db.flush()
        
        for member_id in group_data["member_ids"]:
            member = models.GroupMember(
                group_id=group.id,
                student_id=member_id
            )
            db.add(member)
    
    db.commit()
    
    print(f"✓ Created {len(students)} students")
    print(f"✓ Created {len(groups_data)} study groups")
    print("Database seeding completed!")

def main():
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
