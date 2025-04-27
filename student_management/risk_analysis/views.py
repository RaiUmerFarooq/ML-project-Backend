import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from attendance.models import Student, Attendance, Marks, Course
from attendance.serializers import CourseSerializer
from django.db.models import Avg, Count
from .models import StudentRisk
from .permissions import IsTeacher
from django.utils import timezone
from rest_framework.permissions import AllowAny
import logging

# Set up logging
logger = logging.getLogger(__name__)

class TeacherStudentRiskAnalysis(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        try:
            student = Student.objects.get(name=username)
            attendance_records = Attendance.objects.filter(student=student)
            total_days = attendance_records.count()
            present_days = attendance_records.filter(is_present=True).count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            avg_marks = Marks.objects.filter(student=student).aggregate(Avg('marks'))['marks__avg'] or 0
            assignment_records = Marks.objects.filter(student=student, assessment_type='assignment')
            total_assignments = assignment_records.count()
            submitted_assignments = total_assignments
            assignment_submission_rate = (submitted_assignments / total_assignments * 100) if total_assignments > 0 else 70.0
            engagement_metrics = attendance_percentage
            gpa = (avg_marks / 100) * 4.0

            payload = {
                "attendance": float(attendance_percentage),
                "marks": float(avg_marks),
                "assignment": float(assignment_submission_rate),
                "engagement": float(engagement_metrics),
                "gpa": float(gpa)
            }

            HF_API_URL = "https://ahmadabdulkhaliq-ppas-model-api.hf.space/predict/"
            headers = {"Content-Type": "application/json"}
            response = requests.post(HF_API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                prediction = response.json()
                predicted_grade = prediction.get('predicted_grade', 0.0)
                risk_level = prediction.get('risk_level', 'Unknown')

                StudentRisk.objects.update_or_create(
                    student=student,
                    defaults={
                        'risk_level': risk_level,
                        'confidence': predicted_grade,
                        'last_updated': timezone.now()
                    }
                )

                return Response({
                    "student_id": student.user.id,
                    "username": student.user.username,
                    "name": student.name,
                    "attendance_percentage": round(attendance_percentage, 2),
                    "average_marks": round(avg_marks, 2),
                    "assignment_submission_rate": round(assignment_submission_rate, 2),
                    "engagement_metrics": round(engagement_metrics, 2),
                    "gpa": round(gpa, 2),
                    "risk_prediction": {
                        "risk_level": risk_level,
                        "predicted_grade": predicted_grade,
                        "last_updated": timezone.now()
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Failed to get prediction from Hugging Face Space API",
                    "details": response.text
                }, status=status.HTTP_400_BAD_REQUEST)

        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in TeacherStudentRiskAnalysis: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentRiskAnalysis(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'student':
            return Response({'error': 'Unauthorized access. Only students can access this endpoint.'}, 
                           status=status.HTTP_403_FORBIDDEN)

        try:
            student = Student.objects.get(user=request.user)
            attendance_records = Attendance.objects.filter(student=student)
            total_days = attendance_records.count()
            present_days = attendance_records.filter(is_present=True).count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            avg_marks = Marks.objects.filter(student=student).aggregate(Avg('marks'))['marks__avg'] or 0
            assignment_records = Marks.objects.filter(student=student, assessment_type='assignment')
            total_assignments = assignment_records.count()
            submitted_assignments = total_assignments
            assignment_submission_rate = (submitted_assignments / total_assignments * 100) if total_assignments > 0 else 70.0
            engagement_metrics = attendance_percentage
            gpa = (avg_marks / 100) * 4.0

            payload = {
                "attendance": float(attendance_percentage),
                "marks": float(avg_marks),
                "assignment": float(assignment_submission_rate),
                "engagement": float(engagement_metrics),
                "gpa": float(gpa)
            }

            HF_API_URL = "https://ahmadabdulkhaliq-ppas-model-api.hf.space/predict/"
            headers = {"Content-Type": "application/json"}
            response = requests.post(HF_API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                prediction = response.json()
                predicted_grade = prediction.get('predicted_grade', 0.0)
                risk_level = prediction.get('risk_level', 'Unknown')

                StudentRisk.objects.update_or_create(
                    student=student,
                    defaults={
                        'risk_level': risk_level,
                        'confidence': predicted_grade,
                        'last_updated': timezone.now()
                    }
                )

                return Response({
                    "student_id": student.user.id,
                    "username": student.user.username,
                    "name": student.name,
                    "attendance_percentage": round(attendance_percentage, 2),
                    "average_marks": round(avg_marks, 2),
                    "assignment_submission_rate": round(assignment_submission_rate, 2),
                    "engagement_metrics": round(engagement_metrics, 2),
                    "gpa": round(gpa, 2),
                    "risk_prediction": {
                        "risk_level": risk_level,
                        "predicted_grade": predicted_grade,
                        "last_updated": timezone.now()
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Failed to get prediction from Hugging Face Space API",
                    "details": response.text
                }, status=status.HTTP_400_BAD_REQUEST)

        except Student.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in StudentRiskAnalysis: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomRiskAnalysis(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            required_fields = ['attendance', 'marks', 'assignment', 'engagement', 'gpa', 'username']
            
            if not all(field in data for field in required_fields):
                return Response({
                    "error": "Missing required fields",
                    "required_fields": required_fields
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                payload = {
                    "attendance": float(data['attendance']),
                    "marks": float(data['marks']),
                    "assignment": float(data['assignment']),
                    "engagement": float(data['engagement']),
                    "gpa": float(data['gpa'])
                }
            except (ValueError, TypeError):
                return Response({
                    "error": "Invalid numeric values provided"
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                student = Student.objects.get(name=data['username'])
            except Student.DoesNotExist:
                return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

            HF_API_URL = "https://ahmadabdulkhaliq-ppas-model-api.hf.space/predict/"
            headers = {"Content-Type": "application/json"}
            response = requests.post(HF_API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                prediction = response.json()
                predicted_grade = prediction.get('predicted_grade', 0.0)
                risk_level = prediction.get('risk_level', 'Unknown')

                StudentRisk.objects.update_or_create(
                    student=student,
                    defaults={
                        'risk_level': risk_level,
                        'confidence': predicted_grade,
                        'last_updated': timezone.now()
                    }
                )

                return Response({
                    "student_id": student.user.id,
                    "username": student.user.username,
                    "name": student.name,
                    "input_data": {
                        "attendance": round(payload['attendance'], 2),
                        "average_marks": round(payload['marks'], 2),
                        "assignment_submission_rate": round(payload['assignment'], 2),
                        "engagement_metrics": round(payload['engagement'], 2),
                        "gpa": round(payload['gpa'], 2)
                    },
                    "risk_prediction": {
                        "risk_level": risk_level,
                        "predicted_grade": predicted_grade,
                        "last_updated": timezone.now()
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Failed to get prediction from Hugging Face Space API",
                    "details": response.text
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error in CustomRiskAnalysis: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'student':
            return Response({
                'error': 'Unauthorized access. Only students can access this endpoint.'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            student = Student.objects.get(user=request.user)
            courses = Course.objects.filter(
                attendance__student=student
            ).distinct()
            logger.info(f"Fetched {courses.count()} courses for student {student.roll_number}")
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Student.DoesNotExist:
            logger.warning(f"Student profile not found for user: {request.user.username}")
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in StudentCoursesView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentCourseRiskPredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        if request.user.role != 'student':
            return Response({
                'error': 'Unauthorized access. Only students can access this endpoint.'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            student = Student.objects.get(user=request.user)
            course = Course.objects.get(id=course_id)

            if not Attendance.objects.filter(student=student, subject=course).exists():
                return Response({
                    "error": f"Student is not enrolled in course {course.name}"
                }, status=status.HTTP_400_BAD_REQUEST)

            attendance_records = Attendance.objects.filter(student=student, subject=course)
            total_days = attendance_records.count()
            present_days = attendance_records.filter(is_present=True).count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

            avg_marks = Marks.objects.filter(
                student=student, course=course
            ).aggregate(Avg('marks'))['marks__avg'] or 0

            assignment_records = Marks.objects.filter(
                student=student, course=course, assessment_type='assignment'
            )
            total_assignments = assignment_records.count()
            submitted_assignments = total_assignments
            assignment_submission_rate = (submitted_assignments / total_assignments * 100) if total_assignments > 0 else 70.0

            engagement_metrics = attendance_percentage
            gpa = (avg_marks / 100) * 4.0

            payload = {
                "attendance": float(attendance_percentage),
                "marks": float(avg_marks),
                "assignment": float(assignment_submission_rate),
                "engagement": float(engagement_metrics),
                "gpa": float(gpa)
            }

            HF_API_URL = "https://ahmadabdulkhaliq-ppas-model-api.hf.space/predict/"
            headers = {"Content-Type": "application/json"}
            response = requests.post(HF_API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                prediction = response.json()
                predicted_grade = prediction.get('predicted_grade', 0.0)
                risk_level = prediction.get('risk_level', 'Unknown')

                return Response({
                    "student_id": student.user.id,
                    "username": student.user.username,
                    "name": student.name,
                    "course": {
                        "id": course.id,
                        "name": course.name,
                        "code": course.code
                    },
                    "attendance_percentage": round(attendance_percentage, 2),
                    "average_marks": round(avg_marks, 2),
                    "assignment_submission_rate": round(assignment_submission_rate, 2),
                    "engagement_metrics": round(engagement_metrics, 2),
                    "gpa": round(gpa, 2),
                    "risk_prediction": {
                        "risk_level": risk_level,
                        "predicted_grade": predicted_grade,
                        "last_updated": timezone.now()
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Failed to get prediction from Hugging Face Space API",
                    "details": response.text
                }, status=status.HTTP_400_BAD_REQUEST)

        except Student.DoesNotExist:
            logger.warning(f"Student profile not found for user: {request.user.username}")
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Course.DoesNotExist:
            logger.warning(f"Course with id {course_id} not found")
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in StudentCourseRiskPredictionView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentAllCoursesRiskAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'student':
            return Response({
                'error': 'Unauthorized access. Only students can access this endpoint.'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            student = Student.objects.get(user=request.user)
            attendance_records = Attendance.objects.filter(student=student)
            total_days = attendance_records.count()
            present_days = attendance_records.filter(is_present=True).count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            avg_marks = Marks.objects.filter(student=student).aggregate(Avg('marks'))['marks__avg'] or 0
            assignment_records = Marks.objects.filter(student=student, assessment_type='assignment')
            total_assignments = assignment_records.count()
            submitted_assignments = total_assignments
            assignment_submission_rate = (submitted_assignments / total_assignments * 100) if total_assignments > 0 else 70.0
            engagement_metrics = attendance_percentage
            gpa = (avg_marks / 100) * 4.0

            payload = {
                "attendance": float(attendance_percentage),
                "marks": float(avg_marks),
                "assignment": float(assignment_submission_rate),
                "engagement": float(engagement_metrics),
                "gpa": float(gpa)
            }

            HF_API_URL = "https://ahmadabdulkhaliq-ppas-model-api.hf.space/predict/"
            headers = {"Content-Type": "application/json"}
            response = requests.post(HF_API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                prediction = response.json()
                predicted_grade = prediction.get('predicted_grade', 0.0)
                risk_level = prediction.get('risk_level', 'Unknown')

                StudentRisk.objects.update_or_create(
                    student=student,
                    defaults={
                        'risk_level': risk_level,
                        'confidence': predicted_grade,
                        'last_updated': timezone.now()
                    }
                )

                return Response({
                    "student_id": student.user.id,
                    "username": student.user.username,
                    "name": student.name,
                    "attendance_percentage": round(attendance_percentage, 2),
                    "average_marks": round(avg_marks, 2),
                    "assignment_submission_rate": round(assignment_submission_rate, 2),
                    "engagement_metrics": round(engagement_metrics, 2),
                    "gpa": round(gpa, 2),
                    "risk_prediction": {
                        "risk_level": risk_level,
                        "predicted_grade": predicted_grade,
                        "last_updated": timezone.now()
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Failed to get prediction from Hugging Face Space API",
                    "details": response.text
                }, status=status.HTTP_400_BAD_REQUEST)

        except Student.DoesNotExist:
            logger.warning(f"Student profile not found for user: {request.user.username}")
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in StudentAllCoursesRiskAnalysisView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)