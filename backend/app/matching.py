from sqlalchemy.orm import Session
from . import models
import re
from datetime import datetime

def calculate_match_score(student1: models.Student, student2: models.Student) -> int:
    """Calculate match score based on course, topics, and availability."""
    score = 0
    max_score = 100
    
    # Course match (most important) - 50 points
    if student1.course == student2.course:
        score += 50
    else:
        # Partial credit for related courses (e.g., CS101 and CS201)
        course1_prefix = ''.join([c for c in student1.course if not c.isdigit()])
        course2_prefix = ''.join([c for c in student2.course if not c.isdigit()])
        if course1_prefix == course2_prefix:
            score += 25  # Same department

    # Topics overlap - up to 30 points
    if student1.topics and student2.topics:
        topics1 = set([t.strip().lower() for t in student1.topics.split(",")])
        topics2 = set([t.strip().lower() for t in student2.topics.split(",")])
        
        if topics1 and topics2:
            overlap = len(topics1 & topics2)
            total_unique = len(topics1 | topics2)
            # Jaccard similarity scaled to 30 points
            similarity = overlap / total_unique if total_unique > 0 else 0
            score += int(similarity * 30)

    # Availability overlap - up to 20 points
    if student1.availability and student2.availability:
        # Extract days and time slots
        days1 = set(re.findall(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)', student1.availability))
        days2 = set(re.findall(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)', student2.availability))
        
        if days1 & days2:
            # Common days found - check time overlaps
            common_days = days1 & days2
            time_pattern = r'(\d{1,2})-(\d{1,2})'
            
            time_overlaps = 0
            for day in common_days:
                # Extract time ranges for this day
                times1 = re.findall(time_pattern, student1.availability)
                times2 = re.findall(time_pattern, student2.availability)
                
                # Simple overlap check
                for start1, end1 in times1:
                    for start2, end2 in times2:
                        s1, e1 = int(start1), int(end1)
                        s2, e2 = int(start2), int(end2)
                        if s1 < e2 and s2 < e1:  # Overlap exists
                            time_overlaps += 1
            
            if time_overlaps > 0:
                score += min(time_overlaps * 7, 20)  # Up to 20 points

    return min(score, max_score)

def find_matches(db: Session, student_id: int, limit: int = 10):
    """Find best matches for a student."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        return []

    # Get all other students (prefer same course but show others too)
    other_students = db.query(models.Student).filter(
        models.Student.id != student_id
    ).all()

    matches = []
    for other in other_students:
        # Check if already requested or matched
        existing = db.query(models.MatchRequest).filter(
            ((models.MatchRequest.from_student_id == student_id) & (models.MatchRequest.to_student_id == other.id)) |
            ((models.MatchRequest.from_student_id == other.id) & (models.MatchRequest.to_student_id == student_id))
        ).first()

        if existing and existing.status in ["pending", "accepted"]:
            continue  # Skip if already pending or in a group

        score = calculate_match_score(student, other)
        if score > 0:
            matches.append({
                "student": other,
                "score": score,
                "common_topics": get_common_topics(student, other),
                "common_availability": get_common_availability(student, other)
            })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:limit]

def get_common_topics(student1: models.Student, student2: models.Student) -> str:
    """Get common topics between two students."""
    if not student1.topics or not student2.topics:
        return ""
    topics1 = set([t.strip() for t in student1.topics.split(",")])
    topics2 = set([t.strip() for t in student2.topics.split(",")])
    common = topics1 & topics2
    return ", ".join(common) if common else ""

def get_common_availability(student1: models.Student, student2: models.Student) -> str:
    """Get common available days."""
    if not student1.availability or not student2.availability:
        return ""
    days1 = set(re.findall(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)', student1.availability))
    days2 = set(re.findall(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)', student2.availability))
    common = days1 & days2
    return ", ".join(common) if common else ""

def create_group_from_match(db: Session, request_id: int):
    """Create a study group from an accepted match."""
    match_request = db.query(models.MatchRequest).filter(models.MatchRequest.id == request_id).first()
    if not match_request or match_request.status != "accepted":
        return None

    student1 = match_request.from_student
    student2 = match_request.to_student

    group_name = f"{student1.course} Study Group: {student1.name} & {student2.name}"

    group = models.Group(
        name=group_name,
        course=student1.course
    )
    db.add(group)
    db.flush()

    group_member1 = models.GroupMember(group_id=group.id, student_id=student1.id)
    group_member2 = models.GroupMember(group_id=group.id, student_id=student2.id)
    db.add(group_member1)
    db.add(group_member2)
    
    # Update student stats
    student1.groups_joined = (student1.groups_joined or 0) + 1
    student2.groups_joined = (student2.groups_joined or 0) + 1
    student1.matches_accepted = (student1.matches_accepted or 0) + 1
    student2.matches_accepted = (student2.matches_accepted or 0) + 1
    
    db.commit()

    return group