from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings

from .forms import (
    UserRegistrationForm, LoginForm, AppointmentForm,
    AddNotesForm, UserUpdateForm
)
from .models import User, Appointment

from django.core.mail import send_mail
from django.http import HttpResponse

def test_email(request):
    send_mail(
        'Test Email Django',
        'Ceci est un test d’envoi d’email depuis Django.',
        'attadiagne45@gmail.com',
        ['attadiagne7@gmail.com'],  
        fail_silently=False,
    )
    return HttpResponse("Email envoyé ! Vérifie ta boîte de réception.")


@login_required
def add_notes(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)

    if request.method == 'POST':
        form = AddNotesForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            appointment.status = 'COMPLETED'  # Marque comme terminé
            appointment.save()
            messages.success(request, "Notes médicales ajoutées avec succès.")
            return redirect('dashboard')
    else:
        form = AddNotesForm(instance=appointment)

    return render(request, 'app/add_notes.html', {
        'form': form,
        'appointment': appointment
    })

def home(request):
    return render(request, 'app/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Inscription réussie !')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'app/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Vous êtes connecté(e) en tant que {username}.")
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'app/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "Vous vous êtes déconnecté(e) avec succès.")
    return redirect('home')

@login_required
def dashboard(request):
    if request.user.role == 'PATIENT':
        appointments = Appointment.objects.filter(patient=request.user)
        return render(request, 'app/patient_dashboard.html', {'appointments': appointments})
    elif request.user.role == 'DOCTOR':
        appointments = Appointment.objects.filter(doctor=request.user)
        return render(request, 'app/doctor_dashboard.html', {'appointments': appointments})
    else:
        return redirect('admin:index')

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.user, request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()

            # Envoi de l'email de confirmation
            subject = "Confirmation de votre rendez-vous"
            message = (
                f"Bonjour {appointment.patient.first_name},\n\n"
                f"Votre rendez-vous avec Dr. {appointment.doctor.get_full_name()} "
                f"a bien été enregistré pour le {appointment.date} à {appointment.time}.\n\n"
                "Merci de votre confiance."
            )
            recipient_list = [appointment.patient.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

            messages.success(request, 'Rendez-vous réservé avec succès ! Un email de confirmation a été envoyé.')
            return redirect('dashboard')
    else:
        form = AppointmentForm(request.user)
    return render(request, 'app/appointment.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'app/profile.html', {'form': form})

@login_required
def confirm_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Vérifie que le médecin connecté est bien celui du rendez-vous
    if appointment.doctor != request.user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé(e) à modifier ce rendez-vous.")

    if appointment.status == 'PENDING':
        appointment.status = 'CONFIRMED'
        appointment.save()
        messages.success(request, "Le rendez-vous a été confirmé.")
    return redirect('dashboard')

@login_required
def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Vérifie que le médecin connecté est bien celui du rendez-vous
    if appointment.doctor != request.user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé(e) à modifier ce rendez-vous.")

    if appointment.status == 'PENDING':
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, "Le rendez-vous a été annulé.")
    return redirect('dashboard')

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Vérifie que c’est bien le patient lié à ce rendez-vous
    if appointment.patient != request.user:
        return HttpResponseForbidden("Vous ne pouvez pas annuler ce rendez-vous.")

    # Vérifie que le rendez-vous peut être annulé
    if appointment.status not in ['PENDING', 'CONFIRMED']:
        messages.error(request, "Ce rendez-vous ne peut plus être annulé.")
        return redirect('dashboard')

    if request.method == 'POST':
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, "Votre rendez-vous a été annulé avec succès.")
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Vérifier que c’est bien le patient
    if appointment.patient != request.user:
        return HttpResponseForbidden("Vous ne pouvez pas modifier ce rendez-vous.")

    # On interdit la modification si annulé ou terminé
    if appointment.status in ['CANCELLED', 'COMPLETED']:
        messages.error(request, "Ce rendez-vous ne peut plus être modifié.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = AppointmentForm(request.user, request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre rendez-vous a été mis à jour avec succès.")
            return redirect('dashboard')
    else:
        form = AppointmentForm(request.user, instance=appointment)

    return render(request, 'app/edit_appointment.html', {'form': form, 'appointment': appointment})


