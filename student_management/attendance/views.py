from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Student, Attendance, Marks, Course
from .serializers import StudentSerializer, AttendanceSerializer, MarksSerializer, CourseSerializer
from .permissions import IsTeacher
import logging
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
import csv
from io import StringIO
from datetime import datetime
from django.db import IntegrityError
from django.http import HttpResponse

# Set up logging
logger = logging.getLogger(__name__)

# Get the custom user model
User = get_user_model()

# Existing views (unchanged)
class StudentListCreate(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsTeacher]

class StudentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsTeacher]

class CourseListCreate(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsTeacher]

class CourseRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsTeacher]

class AttendanceListCreate(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacher]

class AttendanceRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacher]

class MarksListCreate(generics.ListCreateAPIView):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer
    permission_classes = [IsTeacher]

class MarksRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer
    permission_classes = [IsTeacher]

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

class StudentSearchByRollNumberView(APIView):
    permission_classes = [IsTeacher]
    authentication_classes = [TokenAuthentication]
    def get(self, request, roll_number):
        try:
            logger.info(f"Searching for student with roll_number: {roll_number}")
            student = Student.objects.get(roll_number=roll_number)
            student_serializer = StudentSerializer(student)
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
            logger.warning(f"Student with roll_number {roll_number} not found")
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in StudentSearchByRollNumberView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AllStudentsDetailsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        try:
            logger.info("Fetching all students with details")
            students = Student.objects.all().select_related('user')
            logger.info(f"Found {students.count()} students")
            response_data = []
            for student in students:
                attendance = Attendance.objects.filter(student=student).select_related('subject')
                marks = Marks.objects.filter(student=student).select_related('course')
                student_serializer = StudentSerializer(student)
                attendance_serializer = AttendanceSerializer(attendance, many=True)
                marks_serializer = MarksSerializer(marks, many=True)
                student_data = {
                    "student": student_serializer.data,
                    "attendance": attendance_serializer.data,
                    "marks": marks_serializer.data
                }
                response_data.append(student_data)
            logger.info("Serialized all students data")
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in AllStudentsDetailsView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentCSVUploadView(APIView):
    permission_classes = [IsTeacher]
    authentication_classes = [TokenAuthentication]
    def post(self, request):
        try:
            logger.info("Processing CSV upload")
            if 'file' not in request.FILES:
                logger.error("No file provided in request")
                return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                logger.error("Uploaded file is not a CSV")
                return Response({"error": "File must be a CSV"}, status=status.HTTP_400_BAD_REQUEST)
            file_data = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(StringIO(file_data))
            required_fields = ['username', 'roll_number', 'name', 'subject', 'attendance_percentage', 'marks_obtained', 'total_marks', 'date', 'check_in_time']
            if not all(field in csv_data.fieldnames for field in required_fields):
                logger.error(f"Missing required fields in CSV. Found: {csv_data.fieldnames}")
                return Response({"error": f"CSV must contain {', '.join(required_fields)}"}, status=status.HTTP_400_BAD_REQUEST)
            created_users = []
            updated_students = []
            created_attendance = []
            created_marks = []
            updated_attendance = []
            updated_marks = []
            errors = []
            for row in csv_data:
                try:
                    username = row['username'].strip()
                    roll_number = row['roll_number'].strip()
                    name = row['name'].strip()
                    subject_name = row['subject'].strip()
                    try:
                        attendance_percentage = float(row['attendance_percentage'])
                        if not 0 <= attendance_percentage <= 100:
                            raise ValueError("Attendance percentage must be between 0 and 100")
                    except ValueError as e:
                        logger.error(f"Invalid attendance_percentage in row for {username}: {str(e)}")
                        errors.append(f"Invalid attendance_percentage for {username}: {str(e)}")
                        continue
                    try:
                        marks_obtained = float(row['marks_obtained'])
                        total_marks = float(row['total_marks'])
                        if marks_obtained < 0 or total_marks <= 0 or marks_obtained > total_marks:
                            raise ValueError("Invalid marks: marks_obtained must be non-negative and not exceed total_marks")
                    except ValueError as e:
                        logger.error(f"Invalid marks in row for {username}: {str(e)}")
                        errors.append(f"Invalid marks for {username}: {str(e)}")
                        continue
                    try:
                        date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    except ValueError:
                        logger.error(f"Invalid date format in row for {username}: {row['date']}")
                        errors.append(f"Invalid date format for {username}: {row['date']}")
                        continue
                    try:
                        check_in_time = datetime.strptime(row['check_in_time'], '%H:%M:%S').time()
                    except ValueError:
                        logger.error(f"Invalid check_in_time format in row for {username}: {row['check_in_time']}")
                        errors.append(f"Invalid check_in_time format for {username}: {row['check_in_time']}")
                        continue
                    try:
                        user = User.objects.get(username=username)
                        if user.role != 'student':
                            logger.error(f"User {username} exists but is not a student (role: {user.role})")
                            errors.append(f"User {username} is not a student (role: {user.role})")
                            continue
                        logger.info(f"Found existing user: {username}")
                    except User.DoesNotExist:
                        try:
                            user = User.objects.create(
                                username=username,
                                first_name=name.split()[0],
                                last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                                role='student'
                            )
                            user.set_password('password123')
                            user.save()
                            created_users.append(username)
                            logger.info(f"Created user: {username}")
                        except IntegrityError as e:
                            logger.error(f"Error creating user {username}: {str(e)}")
                            errors.append(f"Cannot create user {username}: {str(e)}")
                            continue
                    try:
                        student = Student.objects.get(user=user)
                        logger.info(f"Found existing student: {roll_number} - {name}")
                        if student.name != name or student.roll_number != roll_number:
                            if student.roll_number != roll_number and Student.objects.filter(roll_number=roll_number).exists():
                                logger.error(f"Roll number {roll_number} already exists for another student")
                                errors.append(f"Roll number {roll_number} already exists for another student")
                                continue
                            student.name = name
                            student.roll_number = roll_number
                            student.save()
                            updated_students.append(roll_number)
                            logger.info(f"Updated student: {roll_number} - {name}")
                    except Student.DoesNotExist:
                        try:
                            student = Student.objects.create(
                                user=user,
                                name=name,
                                roll_number=roll_number
                            )
                            updated_students.append(roll_number)
                            logger.info(f"Created student: {roll_number} - {name}")
                        except IntegrityError as e:
                            logger.error(f"Integrity error creating student {roll_number}: {str(e)}")
                            errors.append(f"Cannot create student {roll_number}: User already has a student profile")
                            continue
                    try:
                        course, course_created = Course.objects.get_or_create(
                            name=subject_name,
                            defaults={'code': subject_name[:10].upper()}
                        )
                        if course_created:
                            logger.info(f"Created course: {subject_name}")
                    except IntegrityError as e:
                        logger.error(f"Error creating course {subject_name}: {str(e)}")
                        errors.append(f"Cannot create course {subject_name}: {str(e)}")
                        continue
                    is_present = attendance_percentage >= 75
                    try:
                        attendance, attendance_created = Attendance.objects.get_or_create(
                            student=student,
                            subject=course,
                            date=date,
                            defaults={
                                'is_present': is_present,
                            }
                        )
                        if attendance_created:
                            created_attendance.append(f"{roll_number} - {subject_name}")
                            logger.info(f"Created attendance for {roll_number} in {subject_name}")
                        else:
                            attendance.is_present = is_present
                            attendance.save()
                            updated_attendance.append(f"{roll_number} - {subject_name}")
                            logger.info(f"Updated attendance for {roll_number} in {subject_name}")
                    except IntegrityError as e:
                        logger.error(f"Error processing attendance for {roll_number} in {subject_name}: {str(e)}")
                        errors.append(f"Cannot process attendance for {roll_number} in {subject_name}: {str(e)}")
                        continue
                    try:
                        marks, marks_created = Marks.objects.get_or_create(
                            student=student,
                            course=course,
                            assessment_type='quiz',
                            assessment_number=1,
                            date=date,
                            defaults={
                                'marks': marks_obtained,
                                'max_marks': total_marks
                            }
                        )
                        if marks_created:
                            created_marks.append(f"{roll_number} - {subject_name}")
                            logger.info(f"Created marks for {roll_number} in {subject_name}")
                        else:
                            marks.marks = marks_obtained
                            marks.max_marks = total_marks
                            marks.save()
                            updated_marks.append(f"{roll_number} - {subject_name}")
                            logger.info(f"Updated marks for {roll_number} in {subject_name}")
                    except IntegrityError as e:
                        logger.error(f"Error processing marks for {roll_number} in {subject_name}: {str(e)}")
                        errors.append(f"Cannot process marks for {roll_number} in {subject_name}: {str(e)}")
                        continue
                except Exception as e:
                    logger.error(f"Error processing row for {username}: {str(e)}")
                    errors.append(f"Error processing row for {username}: {str(e)}")
                    continue
            logger.info("CSV processing completed")
            if errors:
                return Response({
                    "message": "CSV processed with errors",
                    "created_users": created_users,
                    "updated_students": updated_students,
                    "created_attendance": created_attendance,
                    "updated_attendance": updated_attendance,
                    "created_marks": created_marks,
                    "updated_marks": updated_marks,
                    "errors": errors
                }, status=status.HTTP_207_MULTI_STATUS)
            return Response({
                "message": "CSV processed successfully",
                "created_users": created_users,
                "updated_students": updated_students,
                "created_attendance": created_attendance,
                "updated_attendance": updated_attendance,
                "created_marks": created_marks,
                "updated_marks": updated_marks
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error in StudentCSVUploadView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Updated view for student to export their own data as CSV
class StudentOwnDataCSVExportView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        try:
            logger.info(f"Generating CSV export for user: {request.user.username}")
            # Fetch the student profile for the authenticated user
            student = Student.objects.get(user=request.user)
            if request.user.role != 'student':
                logger.warning(f"User {request.user.username} is not a student (role: {request.user.role})")
                return Response({"error": "Only students can access this endpoint"}, status=status.HTTP_403_FORBIDDEN)

            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{student.roll_number}_data.csv"'

            # Define CSV writer and headers
            writer = csv.writer(response)
            writer.writerow([
                'username', 'first_name', 'last_name', 'roll_number', 'name',
                'subject', 'attendance_date', 'is_present', 'checkin_time', 'attendance_percentage',
                'marks_course', 'assessment_type', 'assessment_number', 'marks', 'max_marks', 'marks_date'
            ])

            # Fetch attendance and marks
            attendance_records = Attendance.objects.filter(student=student).select_related('subject')
            marks_records = Marks.objects.filter(student=student).select_related('course')

            # Calculate overall attendance percentage
            total_attendance = attendance_records.count()
            present_count = attendance_records.filter(is_present=True).count()
            attendance_percentage = round((present_count / total_attendance) * 100, 2) if total_attendance > 0 else 0.0

            logger.info(f"Fetched {len(attendance_records)} attendance records and {len(marks_records)} marks records for {student.roll_number}")

            # If no attendance or marks, include student info only
            if not attendance_records and not marks_records:
                writer.writerow([
                    student.user.username,
                    student.user.first_name,
                    student.user.last_name,
                    student.roll_number,
                    student.name,
                    '', '', '', '', attendance_percentage,
                    '', '', '', '', ''
                ])
            else:
                # Handle attendance and marks pairing
                max_records = max(len(attendance_records), len(marks_records))
                for i in range(max_records):
                    row = [
                        student.user.username,
                        student.user.first_name,
                        student.user.last_name,
                        student.roll_number,
                        student.name
                    ]
                    # Attendance data
                    if i < len(attendance_records):
                        att = attendance_records[i]
                        checkin_time = att.checkin_time.strftime('%H:%M:%S') if att.checkin_time else ''
                        row.extend([
                            att.subject.name,
                            att.date.strftime('%Y-%m-%d'),
                            '1' if att.is_present else '0',
                            checkin_time,
                            attendance_percentage
                        ])
                    else:
                        row.extend(['', '', '', '', attendance_percentage])
                    # Marks data
                    if i < len(marks_records):
                        mark = marks_records[i]
                        row.extend([
                            mark.course.name,
                            mark.assessment_type,
                            mark.assessment_number,
                            mark.marks,
                            mark.max_marks,
                            mark.date.strftime('%Y-%m-%d')
                        ])
                    else:
                        row.extend(['', '', '', '', ''])
                    writer.writerow(row)

            logger.info(f"CSV export generated successfully for {student.roll_number}")
            return response
        except Student.DoesNotExist:
            logger.warning(f"Student profile not found for user: {request.user.username}")
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in StudentOwnDataCSVExportView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)