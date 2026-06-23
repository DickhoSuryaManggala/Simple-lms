from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.core.cache import cache
from django.conf import settings
from ninja import NinjaAPI, Router, Query
from ninja.pagination import paginate
from ninja.errors import HttpError
from .models import Course, Category, Enrollment, Lesson, Progress
from .schemas import (
    RegisterSchema, LoginSchema, TokenSchema, UserSchema, ProfileUpdateSchema,
    CourseListSchema, CourseDetailSchema, CourseCreateSchema,
    EnrollmentSchema, ProgressUpdateSchema, CategorySchema, LessonSchema
)
from config.auth import GlobalAuth, create_access_token, create_refresh_token, decode_token
from .permissions import is_instructor, is_admin, is_student
from django.utils import timezone
from .tasks import send_enrollment_email, update_course_statistics, export_course_report, generate_certificate
from config.mongodb import (
    get_activity_logs_collection,
    get_activity_summary_by_type,
    get_activity_summary_by_user,
    get_course_enrollment_summary,
    get_recent_activity
)
from datetime import datetime

api = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
    description="REST API for Simple LMS with JWT Auth, Redis Caching, and Celery",
    auth=GlobalAuth()
)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_rate_limit(request):
    ip = get_client_ip(request)
    key = f"rate_limit:{ip}"
    current = cache.get(key, 0)
    if current >= settings.RATE_LIMIT_REQUESTS:
        raise HttpError(429, "Too many requests")
    cache.set(key, current + 1, settings.RATE_LIMIT_PERIOD)

def log_activity(user_id, activity_type, data=None):
    activity_logs = get_activity_logs_collection()
    activity_logs.insert_one({
        "user_id": user_id,
        "type": activity_type,
        "data": data or {},
        "timestamp": datetime.utcnow()
    })

@api.get("/", auth=None)
def api_root(request):
    check_rate_limit(request)
    return {"ok": True, "docs_url": "/api/docs"}

# --- Authentication Endpoints ---
auth_router = Router()

@auth_router.post("/register", response={201: UserSchema}, auth=None)
def register(request, data: RegisterSchema):
    check_rate_limit(request)
    if User.objects.filter(username=data.username).exists():
        raise HttpError(400, "Username already exists")
    
    user = User.objects.create_user(
        username=data.username,
        email=data.email,
        password=data.password
    )
    
    group, _ = Group.objects.get_or_create(name=data.role)
    user.groups.add(group)
    log_activity(user.id, "user_registered")
    return user

@auth_router.post("/login", response=TokenSchema, auth=None)
def login(request, data: LoginSchema):
    check_rate_limit(request)
    user = authenticate(username=data.username, password=data.password)
    if not user:
        raise HttpError(401, "Invalid credentials")
    
    access = create_access_token({"user_id": user.id})
    refresh = create_refresh_token({"user_id": user.id})
    log_activity(user.id, "user_logged_in")
    return {"access": access, "refresh": refresh}

@auth_router.post("/refresh", response=TokenSchema, auth=None)
def refresh_token(request, refresh_token: str):
    check_rate_limit(request)
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HttpError(401, "Invalid refresh token")
    
    user_id = payload.get("user_id")
    access = create_access_token({"user_id": user_id})
    refresh = create_refresh_token({"user_id": user_id})
    return {"access": access, "refresh": refresh}

@auth_router.get("/me", response=UserSchema)
def get_me(request):
    check_rate_limit(request)
    return request.user

@auth_router.put("/me", response=UserSchema)
def update_profile(request, data: ProfileUpdateSchema):
    check_rate_limit(request)
    user = request.user
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(user, attr, value)
    user.save()
    log_activity(user.id, "profile_updated")
    return user

# --- Courses Endpoints ---
course_router = Router()

@course_router.get("/", response=List[CourseListSchema], auth=None)
@paginate
def list_courses(request, category_id: Optional[int] = None, search: Optional[str] = None):
    check_rate_limit(request)
    qs = Course.objects.for_listing()
    if category_id:
        qs = qs.filter(category_id=category_id)
    if search:
        qs = qs.filter(title__icontains=search)
    
    result = []
    for course in qs:
        result.append(CourseListSchema(
            id=course.id,
            title=course.title,
            category=CategorySchema(id=course.category.id, name=course.category.name) if course.category else None,
            instructor=course.instructor.username,
            lessons_count=course.lessons_count
        ))
    return result

@course_router.get("/{course_id}", response=CourseDetailSchema, auth=None)
def course_detail(request, course_id: int):
    check_rate_limit(request)
    course = Course.objects.prefetch_related('lessons').get(id=course_id)
    
    lessons = []
    for lesson in course.lessons.all():
        lessons.append(LessonSchema(
            id=lesson.id,
            title=lesson.title,
            content=lesson.content,
            order=lesson.order
        ))
    
    log_activity(None, "course_viewed", {"course_id": course_id})
    return CourseDetailSchema(
        id=course.id,
        title=course.title,
        description=course.description,
        category=CategorySchema(id=course.category.id, name=course.category.name) if course.category else None,
        instructor=course.instructor.username,
        lessons=lessons
    )

@course_router.post("/", response={201: CourseDetailSchema})
@is_instructor
def create_course(request, data: CourseCreateSchema):
    check_rate_limit(request)
    course = Course.objects.create(
        title=data.title,
        description=data.description,
        instructor=request.user,
        category_id=data.category_id
    )
    
    lessons = []
    for lesson in course.lessons.all():
        lessons.append(LessonSchema(
            id=lesson.id,
            title=lesson.title,
            content=lesson.content,
            order=lesson.order
        ))
    
    log_activity(request.user.id, "course_created", {"course_id": course.id})
    return CourseDetailSchema(
        id=course.id,
        title=course.title,
        description=course.description,
        category=CategorySchema(id=course.category.id, name=course.category.name) if course.category else None,
        instructor=course.instructor.username,
        lessons=lessons
    )

@course_router.patch("/{course_id}", response=CourseDetailSchema)
@is_instructor
def update_course(request, course_id: int, data: CourseCreateSchema):
    check_rate_limit(request)
    course = Course.objects.get(id=course_id)
    if course.instructor != request.user and not request.user.is_superuser:
        raise HttpError(403, "You are not the owner of this course")
    
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(course, attr, value)
    course.save()
    
    lessons = []
    for lesson in course.lessons.all():
        lessons.append(LessonSchema(
            id=lesson.id,
            title=lesson.title,
            content=lesson.content,
            order=lesson.order
        ))
    
    log_activity(request.user.id, "course_updated", {"course_id": course_id})
    return CourseDetailSchema(
        id=course.id,
        title=course.title,
        description=course.description,
        category=CategorySchema(id=course.category.id, name=course.category.name) if course.category else None,
        instructor=course.instructor.username,
        lessons=lessons
    )

@course_router.delete("/{course_id}")
@is_admin
def delete_course(request, course_id: int):
    check_rate_limit(request)
    course = Course.objects.get(id=course_id)
    course.delete()
    
    log_activity(request.user.id, "course_deleted", {"course_id": course_id})
    return {"success": True}

# --- Enrollments Endpoints ---
enroll_router = Router()

@enroll_router.post("/", response={201: EnrollmentSchema})
@is_student
def enroll_course(request, course_id: int):
    check_rate_limit(request)
    if Enrollment.objects.filter(student=request.user, course_id=course_id).exists():
        raise HttpError(400, "Already enrolled")
    
    enrollment = Enrollment.objects.create(
        student=request.user,
        course_id=course_id
    )
    send_enrollment_email.delay(enrollment.id)
    log_activity(request.user.id, "course_enrolled", {"course_id": course_id, "enrollment_id": enrollment.id})
    return enrollment

@enroll_router.get("/my-courses", response=List[EnrollmentSchema])
@is_student
def my_courses(request):
    check_rate_limit(request)
    enrollments = Enrollment.objects.for_student_dashboard(request.user)
    
    result = []
    for enrollment in enrollments:
        result.append(EnrollmentSchema(
            id=enrollment.id,
            course_title=enrollment.course.title,
            enrolled_at=enrollment.enrolled_at,
            progress_percentage=enrollment.progress_percentage
        ))
    return result

@enroll_router.post("/{lesson_id}/progress", response={200: dict})
@is_student
def update_progress(request, lesson_id: int, data: ProgressUpdateSchema):
    check_rate_limit(request)
    lesson = Lesson.objects.get(id=lesson_id)
    if not Enrollment.objects.filter(student=request.user, course=lesson.course).exists():
        raise HttpError(403, "Not enrolled in this course")
    
    progress, created = Progress.objects.update_or_create(
        student=request.user,
        lesson=lesson,
        defaults={
            'is_completed': data.is_completed,
            'completed_at': timezone.now() if data.is_completed else None
        }
    )
    
    log_activity(request.user.id, "progress_updated", {"lesson_id": lesson_id, "is_completed": data.is_completed})
    return {"success": True, "is_completed": progress.is_completed}

# --- Analytics & Reports Endpoints ---
analytics_router = Router()

@analytics_router.get("/activity/summary-by-type", auth=None)
def activity_summary_by_type(request):
    check_rate_limit(request)
    return get_activity_summary_by_type()

@analytics_router.get("/activity/summary-by-user", auth=None)
def activity_summary_by_user(request):
    check_rate_limit(request)
    return get_activity_summary_by_user()

@analytics_router.get("/course-enrollment-summary", auth=None)
def course_enrollment_summary(request):
    check_rate_limit(request)
    return get_course_enrollment_summary()

@analytics_router.get("/recent-activity", auth=None)
def recent_activity(request, days: int = 7):
    check_rate_limit(request)
    return get_recent_activity(days=days)

@analytics_router.post("/trigger-update-stats")
@is_admin
def trigger_update_stats(request):
    check_rate_limit(request)
    update_course_statistics.delay()
    return {"success": True, "message": "Course statistics update started"}

@analytics_router.post("/export-report/{course_id}")
@is_instructor
def export_course_report(request, course_id: int):
    check_rate_limit(request)
    export_course_report.delay(course_id)
    return {"success": True, "message": "Course report export started"}

@analytics_router.post("/generate-certificate/{enrollment_id}")
@is_student
def generate_certificate_endpoint(request, enrollment_id: int):
    check_rate_limit(request)
    generate_certificate.delay(enrollment_id)
    return {"success": True, "message": "Certificate generation started"}

api.add_router("/auth", auth_router)
api.add_router("/courses", course_router)
api.add_router("/enrollments", enroll_router)
api.add_router("/analytics", analytics_router)
