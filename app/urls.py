from django.urls import path
from . import views
from .views import RegisterView, RendezVousListCreateView, RendezVousDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import tableau_de_bord_medecin

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', views.home, name='home'),
    path('rendezvous/', RendezVousListCreateView.as_view(), name='rendezvous-list-create'),
    path('rendezvous/<int:pk>/', RendezVousDetailView.as_view(), name='rendezvous-detail'),
     path('medecin/dashboard/', tableau_de_bord_medecin, name='tableau-de-bord-medecin'),
]
