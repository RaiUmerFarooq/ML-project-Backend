import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from attendance.models import Student, Attendance, Marks
from django.db.models import Avg, Count
from .models import StudentRisk
from django.utils import timezone

class TeacherStudentRiskAnalysis(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        # Restrict access to teachers only
        if request.user.role != 'teacher':
            return Response({'error': 'Unauthorized access. Only teachers can access this endpoint.'}, 
                           status=status.HTTP_403_FORBIDDEN)

        try:
            # Get the student by username
            student = Student.objects.get(user__username=username)

            # Calculate attendance percentage
            attendance_records = Attendance.objects.filter(student=student)
            total_days = attendance_records.count()
            present_days = attendance_records.filter(is_present=True).count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

            # Calculate average marks
            avg_marks = Marks.objects.filter(student=student).aggregate(Avg('marks'))['marks__avg'] or 0

            # Approximate assignment submission rate
            # Assumption: Use the count of assignments submitted (we'll assume all Marks entries of type 'assignment' are submitted)
            assignment_records = Marks.objects.filter(student=student, assessment_type='assignment')
            total_assignments = assignment_records.count()
            submitted_assignments = total_assignments  # Assuming all recorded assignments are submitted
            assignment_submission_rate = (submitted_assignments / total_assignments * 100) if total_assignments > 0 else 70.0

            # Approximate engagement metrics
            # Assumption: Use attendance percentage as a proxy for engagement (can be improved with more data)
            engagement_metrics = attendance_percentage

            # Approximate historical GPA
            # Assumption: Convert average marks to a 4.0 scale (e.g., 100% -> 4.0, 50% -> 2.0)
            gpa = (avg_marks / 100) * 4.0

            # Prepare data for Hugging Face Space API
            payload = {
                "attendance": float(attendance_percentage),
                "marks": float(avg_marks),
                "assignment": float(assignment_submission_rate),
                "engagement": float(engagement_metrics),
                "gpa": float(gpa)
            }

            # Hugging Face Space API configuration
            HF_API_URL = "https://raiumer-ppas-model-api.hf.space/predict/"

            headers = {
                "Content-Type": "application/json"
            }

            # Send request to Hugging Face Space API
            response = requests.post(HF_API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                prediction = response.json()
                predicted_grade = prediction.get('predicted_grade', 0.0)
                risk_level = prediction.get('risk_level', 'Unknown')

                # Create or update risk data
                StudentRisk.objects.update_or_create(
                    student=student,
                    defaults={
                        'risk_level': risk_level,
                        'confidence': predicted_grade,  # Using predicted_grade as confidence for simplicity
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
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentRiskAnalysis(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Restrict access to students only
        if request.user.role != 'student':
            return Response({'error': 'Unauthorized access. Only students can access this endpoint.'}, 
                           status=status.HTTP_403_FORBIDDEN)

        try:
            # Get the student associated with the authenticated user
            student = Student.objects.get(user=request.user)

            # Calculate attendance percentage
            attendance_records = Attendance.objects.filter(student=student)
            total_days = attendance_records.count()
            present_days = attendance_records.filter(is_present=True).count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

            # Calculate average marks
            avg_marks = Marks.objects.filter(student=student).aggregate(Avg('marks'))['marks__avg'] or 0

            # Approximate assignment submission rate
            assignment_records = Marks.objects.filter(student=student, assessment_type='assignment')
            total_assignments = assignment_records.count()
            submitted_assignments = total_assignments
            assignment_submission_rate = (submitted_assignments / total_assignments * 100) if total_assignments > 0 else 70.0

            # Approximate engagement metrics
            engagement_metrics = attendance_percentage

            # Approximate historical GPA
            gpa = (avg_marks / 100) * 4.0

            # Prepare data for Hugging Face Space API
            payload = {
                "attendance": float(attendance_percentage),
                "marks": float(avg_marks),
                "assignment": float(assignment_submission_rate),
                "engagement": float(engagement_metrics),
                "gpa": float(gpa)
            }

            # Hugging Face Space API configuration
            HF_API_URL = "https://raiumer-ppas-model-api.hf.space/predict/"

            headers = {
                "Content-Type": "application/json"
            }

            # Send request to Hugging Face Space API
            response = requests.post(HF_API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                prediction = response.json()
                predicted_grade = prediction.get('predicted_grade', 0.0)
                risk_level = prediction.get('risk_level', 'Unknown')

                # Create or update risk data
                StudentRisk.objects.update_or_create(
                    student=student,
                    defaults={
                        'risk_level': risk_level,
                        'confidence': predicted_grade,  # Using predicted_grade as confidence for simplicity
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
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)