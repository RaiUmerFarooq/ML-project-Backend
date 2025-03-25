from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.StudentListCreate.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentRetrieveUpdateDestroy.as_view(), name='student-detail'),
    path('courses/', views.CourseListCreate.as_view(), name='course-list'),
    path('courses/<int:pk>/', views.CourseRetrieveUpdateDestroy.as_view(), name='course-detail'),
    path('attendance/', views.AttendanceListCreate.as_view(), name='attendance-list'),
    path('attendance/<int:pk>/', views.AttendanceRetrieveUpdateDestroy.as_view(), name='attendance-detail'),
    path('marks/', views.MarksListCreate.as_view(), name='marks-list'),
    path('marks/<int:pk>/', views.MarksRetrieveUpdateDestroy.as_view(), name='marks-detail'),
]