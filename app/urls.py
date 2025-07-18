from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointment/', views.book_appointment, name='appointment'),
    path('profile/', views.profile, name='profile'),
    path('appointment/<int:appointment_id>/confirm/', views.confirm_appointment, name='confirm_appointment'),
    path('appointment/<int:appointment_id>/reject/', views.reject_appointment, name='reject_appointment'),
    path('appointments/<int:appointment_id>/add-notes/', views.add_notes, name='add_notes'),
    path('test-email/', views.test_email, name='test_email'),
    path('appointment/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointment/<int:appointment_id>/edit/', views.edit_appointment, name='edit_appointment'),
]