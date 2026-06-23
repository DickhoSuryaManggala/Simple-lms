from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, Enrollment
from config.mongodb import get_activity_logs_collection, get_learning_analytics_collection
import pandas as pd
from datetime import datetime, timedelta

@shared_task
def send_enrollment_email(enrollment_id):
    try:
        enrollment = Enrollment.objects.select_related('student', 'course').get(id=enrollment_id)
        subject = f"Enrollment Confirmation: {enrollment.course.title}"
        message = f"Hi {enrollment.student.username},\n\nYou have successfully enrolled in {enrollment.course.title}.\n\nHappy learning!"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL or 'noreply@example.com',
            [enrollment.student.email],
            fail_silently=False,
        )
        return f"Enrollment email sent to {enrollment.student.email}"
    except Exception as e:
        return f"Error sending enrollment email: {str(e)}"

@shared_task
def generate_certificate(enrollment_id):
    try:
        enrollment = Enrollment.objects.select_related('student', 'course').get(id=enrollment_id)
        # In a real app, you'd generate a PDF certificate here
        certificate_data = {
            "student": enrollment.student.username,
            "course": enrollment.course.title,
            "generated_at": datetime.utcnow().isoformat(),
            "certificate_id": f"CERT-{enrollment.id}-{int(datetime.utcnow().timestamp())}"
        }
        activity_logs = get_activity_logs_collection()
        activity_logs.insert_one({
            "type": "certificate_generated",
            "data": certificate_data,
            "timestamp": datetime.utcnow()
        })
        return f"Certificate generated for {enrollment.student.username}"
    except Exception as e:
        return f"Error generating certificate: {str(e)}"

@shared_task
def update_course_statistics():
    try:
        courses = Course.objects.all()
        learning_analytics = get_learning_analytics_collection()
        
        for course in courses:
            enrollment_count = course.enrollments.count()
            analytics_data = {
                "course_id": course.id,
                "course_title": course.title,
                "enrollment_count": enrollment_count,
                "updated_at": datetime.utcnow()
            }
            learning_analytics.update_one(
                {"course_id": course.id},
                {"$set": analytics_data},
                upsert=True
            )
        return "Course statistics updated"
    except Exception as e:
        return f"Error updating course statistics: {str(e)}"

@shared_task
def export_course_report(course_id):
    try:
        course = Course.objects.get(id=course_id)
        enrollments = Enrollment.objects.filter(course=course).select_related('student')
        
        data = []
        for enrollment in enrollments:
            data.append({
                "student_username": enrollment.student.username,
                "student_email": enrollment.student.email,
                "enrolled_at": enrollment.enrolled_at.isoformat()
            })
        
        df = pd.DataFrame(data)
        report_path = f"course_report_{course_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(report_path, index=False)
        
        activity_logs = get_activity_logs_collection()
        activity_logs.insert_one({
            "type": "report_exported",
            "course_id": course_id,
            "report_path": report_path,
            "timestamp": datetime.utcnow()
        })
        return f"Course report exported to {report_path}"
    except Exception as e:
        return f"Error exporting course report: {str(e)}"
