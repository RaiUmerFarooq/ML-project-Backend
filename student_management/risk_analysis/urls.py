from django.urls import path
from . import views

urlpatterns = [
    path('student/<int:student_id>/risk/', views.StudentRiskAnalysis.as_view(), name='student-risk'),
]