import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from attendance.models import Student, Attendance, Marks
from django.db.models import Avg, Count
from .models import StudentRisk
from django.utils import timezone

class StudentRiskAnalysis(APIView):
    def get(self, request, student_id):
        try:
            # Get student data
            student = Student.objects.get(id=student_id)
            
            # Calculate attendance percentage
            attendance_records = Attendance.objects.filter(student=student)
            total_days = attendance_records.count()
            present_days = attendance_records.filter(is_present=True).count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            # Calculate average marks
            avg_marks = Marks.objects.filter(student=student).aggregate(Avg('marks'))['marks__avg'] or 0
            
            # Prepare data for Hugging Face API
            payload = {
                "inputs": {
                    "attendance_percentage": attendance_percentage,
                    "average_marks": avg_marks
                }
            }
            
            # Hugging Face API configuration
            HF_API_URL = "https://api-inference.huggingface.co/models/your-username/your-model-name"
            HF_API_TOKEN = "your_hugging_face_api_token"  # Get this from Hugging Face
            
            headers = {
                "Authorization": f"Bearer {HF_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # Send request to Hugging Face
            response = requests.post(HF_API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                risk_prediction = response.json()
                
                # Assuming your HF model returns something like {"risk_level": "low", "confidence": 0.92}
                risk_level = risk_prediction.get('risk_level', 'unknown')
                confidence = risk_prediction.get('confidence', 0.0)
                
                # Create or update risk data
                StudentRisk.objects.update_or_create(
                    student=student,
                    defaults={
                        'risk_level': risk_level,
                        'confidence': confidence,
                        'last_updated': timezone.now()
                    }
                )
                
                return Response({
                    "student_id": student_id,
                    "name": student.name,
                    "attendance_percentage": attendance_percentage,
                    "average_marks": avg_marks,
                    "risk_prediction": {
                        "risk_level": risk_level,
                        "confidence": confidence,
                        "last_updated": timezone.now()
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Failed to get prediction from Hugging Face",
                    "details": response.text
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)