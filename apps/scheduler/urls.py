from django.urls import path
from . import views

urlpatterns = [
    path('api/teachers/', views.teachers_list_api, name='teachers-list-api'),
    path('teacher/', views.test_import, name='teacher-import'),
    path('sessions/', views.test_session_import, name='sessions-import'),
]
