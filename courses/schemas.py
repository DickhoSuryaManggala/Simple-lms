from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# Auth Schemas
class RegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = Field(default="student", pattern="^(admin|instructor|student)$")

class LoginSchema(BaseModel):
    username: str
    password: str

class TokenSchema(BaseModel):
    access: str
    refresh: str

class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_staff: bool
    is_superuser: bool

class ProfileUpdateSchema(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Course Schemas
class CategorySchema(BaseModel):
    id: int
    name: str

class LessonSchema(BaseModel):
    id: int
    title: str
    content: str
    order: int

class CourseListSchema(BaseModel):
    id: int
    title: str
    category: Optional[CategorySchema]
    instructor: str
    lessons_count: int

    @staticmethod
    def resolve_instructor(obj):
        return obj.instructor.username

class CourseDetailSchema(BaseModel):
    id: int
    title: str
    description: str
    category: Optional[CategorySchema]
    instructor: str
    lessons: List[LessonSchema]

    @staticmethod
    def resolve_instructor(obj):
        return obj.instructor.username

class CourseCreateSchema(BaseModel):
    title: str
    description: str
    category_id: int

# Enrollment & Progress Schemas
class EnrollmentSchema(BaseModel):
    id: int
    course_title: str
    enrolled_at: datetime
    progress_percentage: float

    @staticmethod
    def resolve_course_title(obj):
        return obj.course.title

class ProgressUpdateSchema(BaseModel):
    is_completed: bool
