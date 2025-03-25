from rest_framework import serializers
from .models import Student, Attendance, Marks, Course

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class MarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marks
        fields = ['id', 'student', 'course', 'assessment_type', 'assessment_number', 'marks', 'max_marks', 'date']