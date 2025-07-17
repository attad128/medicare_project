from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from .models import RendezVous

class RendezVousSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVous
        fields = '__all__'
        read_only_fields = ['patient']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
class RendezVousSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVous
        fields = '__all__'

    def validate_date_heure(self, value):
        from django.utils.timezone import now
        if value <= now():
            raise serializers.ValidationError("La date et l'heure doivent être dans le futur.")
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if 'notes' in validated_data:
            if user.role != 'medecin' or instance.medecin != user:
                raise serializers.ValidationError("Vous ne pouvez modifier que vos notes si vous êtes médecin.")
        return super().update(instance, validated_data)
