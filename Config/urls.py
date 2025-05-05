"""
URL configuration for CalenderScheduler project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from apps.users import urls
from apps.scheduler.views import test_import,test_session_import,test_export,test_export_pdf, AdminDashboardView, teachers_list_api, test_export_teacher_pdfs, generate_and_export_excel, export_teacher_schedule, TeacherListView
from apps.scheduler.Aview import AssignementView
from apps.scheduler.services.export_services import ExportService
urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/',include(urls)),
    path('teacher/', test_import,name='test-import'),
    path('sessions/',test_session_import,name='test-session-import'),
    path('assignements/',AssignementView.as_view(),name='assignementViewTest'),
    path('generate/',test_export,name='test export'),
    path('timetable/',test_export_pdf,name='test pdf'),
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('api/teachers/', teachers_list_api, name='teachers_list_api'),
    path('export/teacher_pdfs/', test_export_teacher_pdfs, name='export_teacher_pdfs'),
    path('generate/export_excel/', generate_and_export_excel, name='generate_and_export_excel'),
    path('teacher/<int:teacher_id>/schedule/', export_teacher_schedule, name='export_teacher_schedule'),
    
]
