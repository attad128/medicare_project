from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, RendezVous
from django.urls import reverse
from datetime import datetime, timedelta

class RendezVousTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient = User.objects.create_user(
            username='patient1', password='Testpass123!', role='patient'
        )
        self.doctor = User.objects.create_user(
            username='doctor1', password='Testpass123!', role='doctor'
        )

    def test_create_rendezvous(self):
        data = {
            "medecin": self.doctor.id,
            "date_heure": (datetime.now() + timedelta(days=1)).isoformat()
        }

        # Authentifier comme patient pour créer un rendez-vous
        self.client.force_authenticate(user=self.patient)

        response = self.client.post(reverse('rendezvous-list-create'), data, format='json')

        print("RESPONSE STATUS:", response.status_code)
        print("RESPONSE DATA:", response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RendezVous.objects.count(), 1)
        rendezvous = RendezVous.objects.get()
        self.assertEqual(rendezvous.medecin.id, self.doctor.id)
        self.assertEqual(rendezvous.patient.id, self.patient.id)
