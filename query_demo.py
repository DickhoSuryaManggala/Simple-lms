import os
import django
from django.db import connection, reset_queries

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Course, Enrollment
from django.contrib.auth.models import User

def demo_n_plus_one():
    print("\n--- N+1 Problem Demo ---")
    reset_queries()
    
    # This triggers N+1 problem if we access category or instructor for each course
    courses = Course.objects.all()
    print(f"Fetching {courses.count()} courses...")
    
    for course in courses:
        # Each of these might trigger a new query if not selected/prefetched
        print(f"Course: {course.title} | Category: {course.category.name} | Instructor: {course.instructor.username}")
    
    print(f"Total queries: {len(connection.queries)}")

def demo_optimized():
    print("\n--- Optimized Query Demo (select_related) ---")
    reset_queries()
    
    # Using the custom manager method which uses select_related
    courses = Course.objects.for_listing()
    print(f"Fetching {courses.count()} courses with optimization...")
    
    for course in courses:
        print(f"Course: {course.title} | Category: {course.category.name} | Instructor: {course.instructor.username} | Lessons: {course.lessons_count}")
    
    print(f"Total queries: {len(connection.queries)}")

def demo_student_dashboard():
    print("\n--- Student Dashboard Optimization Demo ---")
    reset_queries()
    
    student = User.objects.get(username='student1')
    enrollments = Enrollment.objects.for_student_dashboard(student)
    
    print(f"Dashboard for {student.username}:")
    for enr in enrollments:
        print(f"Course: {enr.course.title} | Progress: {enr.progress_percentage:.1f}% ({enr.completed_lessons_count}/{enr.total_lessons_count} lessons)")
    
    print(f"Total queries: {len(connection.queries)}")

if __name__ == '__main__':
    demo_n_plus_one()
    demo_optimized()
    demo_student_dashboard()
