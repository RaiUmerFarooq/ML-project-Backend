from django.db import models

class Student(models.Model):
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
    date = models.DateField()
    is_present = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('student', 'date')
    
    def __str__(self):
        return f"{self.student.name} - {self.date}"

class Marks(models.Model):
    ASSESSMENT_TYPES = (
        ('assignment', 'Assignment'),
        ('quiz', 'Quiz'),
        ('sessional', 'Sessional'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES, default='quiz')  # Default to 'quiz'
    assessment_number = models.IntegerField(default=1)  # Default to 1st quiz/assignment
    marks = models.FloatField()
    max_marks = models.FloatField(default=100)
    date = models.DateField()
    
    class Meta:
        unique_together = ('student', 'course', 'assessment_type', 'assessment_number', 'date')
    
    def __str__(self):
        return f"{self.student.name} - {self.course.name} - {self.assessment_type} {self.assessment_number} - {self.marks}"