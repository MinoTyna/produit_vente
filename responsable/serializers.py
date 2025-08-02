
from rest_framework import serializers
from .models import Responsable
# serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # sub = identifiant unique dans le payload
        token['sub'] = user.id  # 👈 nécessaire pour que frontend ait l'ID
        token['email'] = user.Responsable_email
        token['nom'] = user.Responsable_nom
        token['role'] = user.Responsable_role
        token['photo'] = user.Responsable_photo.url if user.Responsable_photo else ""


        return token


class ResponsableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsable
        fields = '__all__'
