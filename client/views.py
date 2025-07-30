from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import Client
from .serializers import ClientSerializer
from django.conf import settings
# monbackend/views.py
import requests


# 🔹 GET : Liste des clients
class ClientListAPIView(APIView):
    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 🔹 GET : Total des clients
class ClientTotalAPIView(APIView):
    def get(self, request):
        total_clients = Client.objects.count()
        return Response({"total_clients": total_clients}, status=status.HTTP_200_OK)

class ClientDetailAPIView(APIView):
    def get_object(self, id):
        try:
            return Client.objects.get(id=id)
        except Client.DoesNotExist:
            raise Http404

    def get(self, request, id):
        client = self.get_object(id)
        serializer = ClientSerializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 🔹 POST : Créer un nouveau client
class ClientCreateAPIView(APIView):
    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 🔹 DELETE : Supprimer un client par son id
class ClientDeleteAPIView(APIView):
    def delete(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({"error": "Client introuvable."}, status=status.HTTP_404_NOT_FOUND)

        client.delete()
        return Response({"message": "Client supprimé avec succès."}, status=status.HTTP_200_OK)

class ClientUpdateAPIView(APIView):
    def put(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({"error": "client introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClientSerializer(client, data=request.data, partial=True)  # partial=True pour update partiel
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Client mis à jour avec succès.", "client": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GeocodeAPIView(APIView):
    def get(self, request):
        address = request.GET.get('address')
        if not address:
            return Response({"error": "Adresse non fournie"}, status=status.HTTP_400_BAD_REQUEST)

        api_key = settings.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"

        response = requests.get(url)
        data = response.json()

        if data.get("status") != "OK":
            return Response({"error": data.get("error_message", "Adresse introuvable")}, status=400)

        location = data["results"][0]["geometry"]["location"]
        return Response(location, status=200)