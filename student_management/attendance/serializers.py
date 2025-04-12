from rest_framework import serializers
from .models import User, Student, Attendance, Marks, Course
from django.core.exceptions import ObjectDoesNotExist

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = ['user', 'name', 'roll_number']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code']

class AttendanceSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(write_only=True)  # Accept username or user_id
    subject_id = serializers.IntegerField(write_only=True)  # Accept course ID
    subject = CourseSerializer(read_only=True)  # Include course details in response
    
    class Meta:
        model = Attendance
        fields = ['id', 'student_id', 'subject_id', 'subject', 'date', 'is_present', 'checkin_time']
        read_only_fields = ['id', 'checkin_time', 'subject']

    def validate_student_id(self, value):
        try:
            # Try to find user by username or ID
            try:
                user = User.objects.get(username=value)
            except ValueError:
                user = User.objects.get(id=int(value))
            # Ensure user is a student
            if user.role != 'student':
                raise serializers.ValidationError("User is not a student")
            # Ensure student profile exists
            if not Student.objects.filter(user=user).exists():
                raise serializers.ValidationError("Student profile not found")
            return user
        except ObjectDoesNotExist:
            raise serializers.ValidationError("User not found")

    def validate_subject_id(self, value):
        if not Course.objects.filter(id=value).exists():
            raise serializers.ValidationError("Course not found")
        return value

    def create(self, validated_data):
        user = validated_data.pop('student_id')
        subject_id = validated_data.pop('subject_id')
        student = Student.objects.get(user=user)
        subject = Course.objects.get(id=subject_id)
        return Attendance.objects.create(student=student, subject=subject, **validated_data)

class MarksSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(write_only=True)  # Accept username or user_id
    course_id = serializers.IntegerField(write_only=True)  # Accept course ID
    course = CourseSerializer(read_only=True)  # Include course details in response
    
    class Meta:
        model = Marks
        fields = ['id', 'student_id', 'course_id', 'course', 'assessment_type', 'assessment_number', 'marks', 'max_marks', 'date']
        read_only_fields = ['id', 'course']

    def validate_student_id(self, value):
        try:
            try:
                user = User.objects.get(username=value)
            except ValueError:
                user = User.objects.get(id=int(value))
            if user.role != 'student':
                raise serializers.ValidationError("User is not a student")
            if not Student.objects.filter(user=user).exists():
                raise serializers.ValidationError("Student profile not found")
            return user
        except ObjectDoesNotExist:
            raise serializers.ValidationError("User not found")

    def validate_course_id(self, value):
        if not Course.objects.filter(id=value).exists():
            raise serializers.ValidationError("Course not found")
        return value

    def validate(self, data):
        if data['marks'] > data['max_marks']:
            raise serializers.ValidationError("Marks cannot exceed max_marks")
        return data

    def create(self, validated_data):
        user = validated_data.pop('student_id')
        course_id = validated_data.pop('course_id')
        student = Student.objects.get(user=user)
        course = Course.objects.get(id=course_id)
        return Marks.objects.create(student=student, course=course, **validated_data)