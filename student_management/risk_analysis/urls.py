from django.urls import path
from . import views

app_name = 'risk_analysis'

urlpatterns = [
    path('teacher/risk-analysis/<str:username>/', views.TeacherStudentRiskAnalysis.as_view(), name='teacher-risk-analysis'),
    path('student/risk-analysis/', views.StudentRiskAnalysis.as_view(), name='student-risk-analysis'),
    path('custom/risk-analysis/', views.CustomRiskAnalysis.as_view(), name='custom-risk-analysis'),
    path('student/courses/', views.StudentCoursesView.as_view(), name='student-courses'),
    path('student/course-prediction/<int:course_id>/', views.StudentCourseRiskPredictionView.as_view(), name='student-course-prediction'),
    path('student/all-courses-risk-analysis/', views.StudentAllCoursesRiskAnalysisView.as_view(), name='student-all-courses-risk-analysis'),
]