from rest_framework import generics, permissions
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import RendezVous, User
from .serializers import RendezVousSerializer, RegisterSerializer
from .decorators import role_required

@login_required
@role_required(allowed_roles=['medecin'])
def tableau_de_bord_medecin(request):
    rdvs = RendezVous.objects.filter(medecin=request.user).order_by('date_heure')
    html = "<h1>Tableau de bord Médecin</h1><ul>"
    for rdv in rdvs:
        html += f"<li>{rdv.patient.username} - {rdv.date_heure} - Notes: {rdv.notes or 'Aucune'}</li>"
    html += "</ul>"
    return HttpResponse(html)

class RendezVousListCreateView(generics.ListCreateAPIView):
    serializer_class = RendezVousSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return RendezVous.objects.filter(patient=user)
        elif user.role == 'medecin':
            return RendezVous.objects.filter(medecin=user)
        return RendezVous.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'patient':
            serializer.save(patient=user)
        else:
            raise PermissionError("Seuls les patients peuvent créer un rendez-vous.")

class RendezVousDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RendezVousSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return RendezVous.objects.filter(patient=user)
        elif user.role == 'medecin':
            return RendezVous.objects.filter(medecin=user)
        return RendezVous.objects.none()

class UpdateNoteView(generics.UpdateAPIView):
    serializer_class = RendezVousSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Seul le médecin propriétaire du RDV peut modifier la note
        if user.role == 'medecin':
            return RendezVous.objects.filter(medecin=user)
        return RendezVous.objects.none()

    def patch(self, request, *args, **kwargs):
        # Permet une mise à jour partielle (notes uniquement)
        return self.partial_update(request, *args, **kwargs)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

def home(request):
    return HttpResponse("<h1>Bienvenue sur Medicare 🏥</h1><p>API active.</p>")
