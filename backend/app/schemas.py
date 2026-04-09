from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class StudentCreate(BaseModel):
    name: str
    password: str
    course: str
    topics: Optional[str] = None
    availability: Optional[str] = None
    telegram_id: Optional[str] = None

class StudentLogin(BaseModel):
    name: str
    password: str

class StudentResponse(BaseModel):
    id: int
    name: str
    course: str
    topics: Optional[str]
    availability: Optional[str]
    telegram_id: Optional[str]
    matches_accepted: Optional[int]
    groups_joined: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
    
    # Exclude password_hash from responses
    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        data.pop('password_hash', None)
        return data

class MemberResponse(BaseModel):
    id: int
    name: str
    course: str
    topics: Optional[str]
    availability: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    success: bool
    message: str
    student: Optional[StudentResponse] = None

class MatchRequestCreate(BaseModel):
    to_student_id: int

class MatchRequestResponse(BaseModel):
    id: int
    from_student: StudentResponse
    to_student: StudentResponse
    status: str
    created_at: datetime

class GroupCreate(BaseModel):
    name: str
    course: str
    student_ids: List[int]

class GroupResponse(BaseModel):
    id: int
    name: str
    course: str
    members: List[MemberResponse]
    created_at: datetime

class AIQuestion(BaseModel):
    question: str

class AIResponse(BaseModel):
    answer: str