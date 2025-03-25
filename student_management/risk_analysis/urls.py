from django.urls import path
from .views import StudentRiskAnalysis

urlpatterns = [
    path('student/<int:student_id>/risk/', StudentRiskAnalysis.as_view(), name='student-risk-analysis'),
]