from rest_framework import generics
from .models import Student, Attendance, Marks, Course
from .serializers import StudentSerializer, AttendanceSerializer, MarksSerializer, CourseSerializer

class StudentListCreate(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class CourseListCreate(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class AttendanceListCreate(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class AttendanceRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class MarksListCreate(generics.ListCreateAPIView):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer

class MarksRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer