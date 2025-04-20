from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Student, Attendance, Marks, Course
from .serializers import StudentSerializer, AttendanceSerializer, MarksSerializer, CourseSerializer
from .permissions import IsTeacher
import logging

# Set up logging
logger = logging.getLogger(__name__)

# CRUD for Students
class StudentListCreate(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsTeacher]

class StudentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsTeacher]

# CRUD for Courses
class CourseListCreate(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsTeacher]

class CourseRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsTeacher]

# CRUD for Attendance (Teacher-only)
class AttendanceListCreate(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacher]

class AttendanceRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacher]

# CRUD for Marks (Teacher-only)
class MarksListCreate(generics.ListCreateAPIView):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer
    permission_classes = [IsTeacher]

class MarksRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer
    permission_classes = [IsTeacher]

# Student-specific Attendance
class StudentOwnAttendanceView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
            attendance = Attendance.objects.filter(student=student)
            serializer = AttendanceSerializer(attendance, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in StudentOwnAttendanceView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Student-specific Marks
class StudentOwnMarksView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
            marks = Marks.objects.filter(student=student)
            serializer = MarksSerializer(marks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in StudentOwnMarksView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# All Attendance for Teachers
class AllAttendanceView(APIView):
    permission_classes = [IsTeacher]
    def get(self, request):
        try:
            logger.info("Fetching all attendance records")
            attendance = Attendance.objects.all().select_related('student', 'subject')
            logger.info(f"Found {attendance.count()} attendance records")
            serializer = AttendanceSerializer(attendance, many=True)
            logger.info("Serialized attendance data")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in AllAttendanceView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# All Marks for Teachers
class AllMarksView(APIView):
    permission_classes = [IsTeacher]
    def get(self, request):
        try:
            logger.info("Fetching all marks records")
            marks = Marks.objects.all().select_related('student', 'course')
            logger.info(f"Found {marks.count()} marks records")
            serializer = MarksSerializer(marks, many=True)
            logger.info("Serialized marks data")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in AllMarksView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Search Student by Roll Number (Teacher-only)
class StudentSearchByRollNumberView(APIView):
    permission_classes = [IsTeacher]
    authentication_classes = [TokenAuthentication]
    def get(self, request, roll_number):
        try:
            logger.info(f"Searching for student with roll number: {roll_number}")
            student = Student.objects.get(roll_number=roll_number)
            student_serializer = StudentSerializer(student)
            
            # Fetch related attendance and marks
            attendance = Attendance.objects.filter(student=student).select_related('subject')
            marks = Marks.objects.filter(student=student).select_related('course')
            
            attendance_serializer = AttendanceSerializer(attendance, many=True)
            marks_serializer = MarksSerializer(marks, many=True)
            
            logger.info(f"Found student: {student.name}")
            logger.info(f"Student data: {student_serializer.data}")
            logger.info(f"Attendance data: {attendance_serializer.data}")
            logger.info(f"Marks data: {marks_serializer.data}")
            
            response_data = {
                "student": student_serializer.data,
                "attendance": attendance_serializer.data,
                "marks": marks_serializer.data
            }
            logger.info(f"Response data: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            logger.warning(f"Student with roll number {roll_number} not found")
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in StudentSearchByRollNumberView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)