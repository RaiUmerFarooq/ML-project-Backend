from django.db import models
from attendance.models import Student

class StudentRisk(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    risk_level = models.CharField(max_length=50)
    confidence = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.risk_level}"