from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Responsable
from .serializers import ResponsableSerializer

class SyncResponsableAPIView(APIView):
    def post(self, request):
        data = request.data
        Responsable_email = data.get("Responsable_email")
        if not Responsable_email:
            return Response({"error": "Email requis"}, status=400)

        responsable, created = Responsable.objects.update_or_create(
            Responsable_email=Responsable_email,
            defaults={
                'Responsable_nom': data.get('Responsable_nom'),  # None autorisé
                'Responsable_prenom': data.get('Responsable_prenom'),
                'Responsable_adresse': data.get('Responsable_adresse'),
                'Responsable_telephone': data.get('Responsable_telephone'),
                'Responsable_role': data.get('Responsable_role', 'vendeur'),
            }
        )
        serializer = ResponsableSerializer(responsable)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 🔹 GET : Total des Responsable
class ResponsableTotalAPIView(APIView):
    def get(self, request):
        total_Responsables = Responsable.objects.count()
        return Response({"total_Responsables": total_Responsables}, status=status.HTTP_200_OK)



class ResponsableListAPIView(APIView):
    def get(self, request):
        Responsable_email = request.GET.get('Responsable_email')
        if Responsable_email:
            try:
                responsable = Responsable.objects.get(Responsable_email=Responsable_email)
                serializer = ResponsableSerializer(responsable)
                return Response(serializer.data)
            except Responsable.DoesNotExist:
                return Response({"detail": "Responsable non trouvé"}, status=status.HTTP_404_NOT_FOUND)
        else:
            responsables = Responsable.objects.all()
            serializer = ResponsableSerializer(responsables, many=True)
            return Response(serializer.data)
        
        
class ResponsabletUpdateAPIView(APIView):
    def put(self, request, responsable_id):
        try:
            responsable = Responsable.objects.get(id=responsable_id)
        except Responsable.DoesNotExist:
            return Response({"error": "responsable introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ResponsableSerializer(responsable, data=request.data, partial=True)  # partial=True pour update partiel
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "responsable mis à jour avec succès.", "responsable": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResponsableDetailView(APIView):
    def get(self, request, pk):
        try:
            responsable = Responsable.objects.get(pk=pk)
            serializer = ResponsableSerializer(responsable)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Responsable.DoesNotExist:
            return Response(
                {"detail": "Responsable non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )