from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return self.username

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=True)
    checkin_time = models.TimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'date')
    
    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.date} - {self.checkin_time}"

class Marks(models.Model):
    ASSESSMENT_TYPES = (
        ('assignment', 'Assignment'),
        ('quiz', 'Quiz'),
        ('sessional', 'Sessional'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES, default='quiz')
    assessment_number = models.IntegerField(default=1)
    marks = models.FloatField()
    max_marks = models.FloatField(default=100)
    date = models.DateField()
    
    class Meta:
        unique_together = ('student', 'course', 'assessment_type', 'assessment_number', 'date')
    
    def __str__(self):
        return f"{self.student.name} - {self.course.name} - {self.assessment_type} {self.assessment_number} - {self.marks}"

# Signal to create a Student object when a User with role='student' is created
@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'student':
        # Generate a unique roll_number (e.g., S001, S002, etc.)
        existing_students = Student.objects.count()
        roll_number = f"S{str(existing_students + 1).zfill(3)}"  # e.g., S001, S002
        Student.objects.create(
            user=instance,
            name=instance.username,  # Use username as the default name
            roll_number=roll_number
        )