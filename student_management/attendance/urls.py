from django.urls import path
from . import views, views_auth

urlpatterns = [
    path('students/', views.StudentListCreate.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentRetrieveUpdateDestroy.as_view(), name='student-detail'),
    path('students/search/<str:roll_number>/', views.StudentSearchByRollNumberView.as_view(), name='student-search-by-roll'),
    path('courses/', views.CourseListCreate.as_view(), name='course-list'),
    path('courses/<int:pk>/', views.CourseRetrieveUpdateDestroy.as_view(), name='course-detail'),
    path('attendance/', views.AttendanceListCreate.as_view(), name='attendance-list'),
    path('attendance/<int:pk>/', views.AttendanceRetrieveUpdateDestroy.as_view(), name='attendance-detail'),
    path('marks/', views.MarksListCreate.as_view(), name='marks-list'),
    path('marks/<int:pk>/', views.MarksRetrieveUpdateDestroy.as_view(), name='marks-detail'),
    path('my-attendance/', views.StudentOwnAttendanceView.as_view(), name='my-attendance'),
    path('my-marks/', views.StudentOwnMarksView.as_view(), name='my-marks'),
    path('all-attendance/', views.AllAttendanceView.as_view(), name='all-attendance'),
    path('all-marks/', views.AllMarksView.as_view(), name='all-marks'),
    path('login/', views_auth.LoginView.as_view(), name='login'),
    path('logout/', views_auth.LogoutView.as_view(), name='logout'),
    path('students/all-details/', views.AllStudentsDetailsView.as_view(), name='all-students-details'),
    path('students/upload-csv/', views.StudentCSVUploadView.as_view(), name='student-csv-upload'),
    path('my-data/export-csv/', views.StudentOwnDataCSVExportView.as_view(), name='student-own-data-csv-export'),
    path('teacher/students/export-csv/', views.TeacherStudentDataCSVExportView.as_view(), name='teacher-all-students-data-csv-export'),
    path('teacher/students/export-csv/<str:roll_number>/', views.TeacherStudentDataCSVExportView.as_view(), name='teacher-student-data-csv-export'),
]