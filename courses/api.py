from typing import List, Optional
from django.shortcuts import get_object_or_found
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from ninja import NinjaAPI, Router, Query
from ninja.pagination import paginate
from .models import Course, Category, Enrollment, Lesson, Progress
from .schemas import (
    RegisterSchema, LoginSchema, TokenSchema, UserSchema, ProfileUpdateSchema,
    CourseListSchema, CourseDetailSchema, CourseCreateSchema,
    EnrollmentSchema, ProgressUpdateSchema
)
from config.auth import GlobalAuth, create_access_token, create_refresh_token, decode_token
from .permissions import is_instructor, is_admin, is_student
from django.utils import timezone

api = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
    description="REST API for Simple LMS with JWT Auth",
    auth=GlobalAuth()
)

# --- Authentication Endpoints ---
auth_router = Router()

@auth_router.post("/register", response={201: UserSchema}, auth=None)
def register(request, data: RegisterSchema):
    if User.objects.filter(username=data.username).exists():
        from ninja.errors import HttpError
        raise HttpError(400, "Username already exists")
    
    user = User.objects.create_user(
        username=data.username,
        email=data.email,
        password=data.password
    )
    
    # Assign role
    group, _ = Group.objects.get_or_create(name=data.role)
    user.groups.add(group)
    return user

@auth_router.post("/login", response=TokenSchema, auth=None)
def login(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if not user:
        from ninja.errors import HttpError
        raise HttpError(401, "Invalid credentials")
    
    access = create_access_token({"user_id": user.id})
    refresh = create_refresh_token({"user_id": user.id})
    return {"access": access, "refresh": refresh}

@auth_router.post("/refresh", response=TokenSchema, auth=None)
def refresh_token(request, refresh_token: str):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        from ninja.errors import HttpError
        raise HttpError(401, "Invalid refresh token")
    
    user_id = payload.get("user_id")
    access = create_access_token({"user_id": user_id})
    refresh = create_refresh_token({"user_id": user_id})
    return {"access": access, "refresh": refresh}

@auth_router.get("/me", response=UserSchema)
def get_me(request):
    return request.user

@auth_router.put("/me", response=UserSchema)
def update_profile(request, data: ProfileUpdateSchema):
    user = request.user
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(user, attr, value)
    user.save()
    return user

# --- Courses Endpoints ---
course_router = Router()

@course_router.get("/", response=List[CourseListSchema], auth=None)
@paginate
def list_courses(request, category_id: Optional[int] = None, search: Optional[str] = None):
    qs = Course.objects.for_listing()
    if category_id:
        qs = qs.filter(category_id=category_id)
    if search:
        qs = qs.filter(title__icontains=search)
    return qs

@course_router.get("/{course_id}", response=CourseDetailSchema, auth=None)
def course_detail(request, course_id: int):
    return Course.objects.prefetch_related('lessons').get(id=course_id)

@course_router.post("/", response={201: CourseDetailSchema})
@is_instructor
def create_course(request, data: CourseCreateSchema):
    course = Course.objects.create(
        title=data.title,
        description=data.description,
        instructor=request.user,
        category_id=data.category_id
    )
    return course

@course_router.patch("/{course_id}", response=CourseDetailSchema)
@is_instructor
def update_course(request, course_id: int, data: CourseCreateSchema):
    course = Course.objects.get(id=course_id)
    if course.instructor != request.user and not request.user.is_superuser:
        from ninja.errors import HttpError
        raise HttpError(403, "You are not the owner of this course")
    
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(course, attr, value)
    course.save()
    return course

@course_router.delete("/{course_id}")
@is_admin
def delete_course(request, course_id: int):
    course = Course.objects.get(id=course_id)
    course.delete()
    return {"success": True}

# --- Enrollments Endpoints ---
enroll_router = Router()

@enroll_router.post("/", response={201: EnrollmentSchema})
@is_student
def enroll_course(request, course_id: int):
    if Enrollment.objects.filter(student=request.user, course_id=course_id).exists():
        from ninja.errors import HttpError
        raise HttpError(400, "Already enrolled")
    
    enrollment = Enrollment.objects.create(
        student=request.user,
        course_id=course_id
    )
    return enrollment

@enroll_router.get("/my-courses", response=List[EnrollmentSchema])
@is_student
def my_courses(request):
    return Enrollment.objects.for_student_dashboard(request.user)

@enroll_router.post("/{lesson_id}/progress", response={200: dict})
@is_student
def update_progress(request, lesson_id: int, data: ProgressUpdateSchema):
    lesson = Lesson.objects.get(id=lesson_id)
    # Ensure user is enrolled in the course of this lesson
    if not Enrollment.objects.filter(student=request.user, course=lesson.course).exists():
        from ninja.errors import HttpError
        raise HttpError(403, "Not enrolled in this course")
    
    progress, created = Progress.objects.update_or_create(
        student=request.user,
        lesson=lesson,
        defaults={
            'is_completed': data.is_completed,
            'completed_at': timezone.now() if data.is_completed else None
        }
    )
    return {"success": True, "is_completed": progress.is_completed}

api.add_router("/auth", auth_router)
api.add_router("/courses", course_router)
api.add_router("/enrollments", enroll_router)
