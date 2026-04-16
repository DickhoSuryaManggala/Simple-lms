from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Case, When, FloatField

class CourseQuerySet(models.QuerySet):
    def for_listing(self):
        """Optimized for list view with category and instructor info"""
        return self.select_related('category', 'instructor').annotate(
            lessons_count=Count('lessons')
        )

class EnrollmentQuerySet(models.QuerySet):
    def for_student_dashboard(self, student):
        """Optimized for student dashboard with progress calculation"""
        return self.filter(student=student).select_related('course', 'course__category').annotate(
            completed_lessons_count=Count('course__lessons__progress', filter=models.Q(course__lessons__progress__is_completed=True, course__lessons__progress__student=student)),
            total_lessons_count=Count('course__lessons', distinct=True),
            progress_percentage=Case(
                When(total_lessons_count__gt=0, 
                     then=100.0 * models.F('completed_lessons_count') / models.F('total_lessons_count')),
                default=0.0,
                output_field=FloatField()
            )
        )

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instructed_courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CourseQuerySet.as_manager()

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    objects = EnrollmentQuerySet.as_manager()

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

class Progress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'lesson')
        verbose_name_plural = "Progress"

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.student.username} - {self.lesson.title} ({status})"
