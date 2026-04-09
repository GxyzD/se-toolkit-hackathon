from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)  # Unique usernames
    password_hash = Column(String, nullable=False)  # Hashed password
    course = Column(String, nullable=False)
    topics = Column(String, nullable=True)  # "Python,AI,Web"
    availability = Column(String, nullable=True)  # "Mon 10-12,Wed 14-16"
    telegram_id = Column(String, nullable=True)  # Telegram chat ID for notifications
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    sent_requests = relationship("MatchRequest", foreign_keys="MatchRequest.from_student_id", back_populates="from_student")
    received_requests = relationship("MatchRequest", foreign_keys="MatchRequest.to_student_id", back_populates="to_student")
    groups = relationship("GroupMember", back_populates="student")
    
    # Statistics tracking
    matches_accepted = Column(Integer, default=0)
    groups_joined = Column(Integer, default=0)

class MatchRequest(Base):
    __tablename__ = "match_requests"

    id = Column(Integer, primary_key=True, index=True)
    from_student_id = Column(Integer, ForeignKey("students.id"))
    to_student_id = Column(Integer, ForeignKey("students.id"))
    status = Column(String, default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    from_student = relationship("Student", foreign_keys=[from_student_id], back_populates="sent_requests")
    to_student = relationship("Student", foreign_keys=[to_student_id], back_populates="received_requests")

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    course = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    members = relationship("GroupMember", back_populates="group")

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    group = relationship("Group", back_populates="members")
    student = relationship("Student", back_populates="groups")