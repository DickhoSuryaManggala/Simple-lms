from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

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
    model_config = ConfigDict(from_attributes=True)
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
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class LessonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content: str
    order: int

class CourseListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    category: Optional[CategorySchema]
    instructor: str
    lessons_count: int

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            title=obj.title,
            category=CategorySchema.from_orm(obj.category) if obj.category else None,
            instructor=obj.instructor.username,
            lessons_count=obj.lessons_count
        )

class CourseDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    category: Optional[CategorySchema]
    instructor: str
    lessons: List[LessonSchema]

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            title=obj.title,
            description=obj.description,
            category=CategorySchema.from_orm(obj.category) if obj.category else None,
            instructor=obj.instructor.username,
            lessons=[LessonSchema.from_orm(lesson) for lesson in obj.lessons.all()]
        )

class CourseCreateSchema(BaseModel):
    title: str
    description: str
    category_id: int

# Enrollment & Progress Schemas
class EnrollmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    course_title: str
    enrolled_at: datetime
    progress_percentage: float

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            course_title=obj.course.title,
            enrolled_at=obj.enrolled_at,
            progress_percentage=obj.progress_percentage
        )

class ProgressUpdateSchema(BaseModel):
    is_completed: bool
