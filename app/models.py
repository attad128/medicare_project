from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Administrator'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

    def __str__(self):
        return f"{self.username} ({self.role})"


class RendezVous(models.Model):
    STATUTS = [
        ('reserve', 'Réservé'),
        ('annule', 'Annulé'),
        ('termine', 'Terminé'),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rendezvous_patient',
        limit_choices_to={'role': 'patient'}
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rendezvous_medecin',
        limit_choices_to={'role': 'doctor'}
    )
    date_heure = models.DateTimeField()
    statut = models.CharField(max_length=10, choices=STATUTS, default='reserve')

    def __str__(self):
        return f"RDV {self.id} - {self.patient} avec {self.medecin} le {self.date_heure}"
