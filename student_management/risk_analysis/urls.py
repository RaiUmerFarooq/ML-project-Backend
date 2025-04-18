from django.urls import path
from . import views

app_name = 'risk_analysis'

urlpatterns = [
    path('teacher/risk-analysis/<str:username>/', views.TeacherStudentRiskAnalysis.as_view(), name='teacher-risk-analysis'),
    path('student/risk-analysis/', views.StudentRiskAnalysis.as_view(), name='student-risk-analysis'),
]