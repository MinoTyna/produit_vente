from django.db import models

class Client(models.Model):
    Client_nom = models.CharField(max_length=100, null=True)
    Client_prenom = models.CharField(max_length=100, null=True)
    Client_cin = models.CharField(max_length=12, unique=True, null=True)
    Client_photo = models.ImageField(upload_to='clients/photos/', blank=True, null=True)
    Client_adresse = models.TextField(null=True)
    Client_quartier = models.CharField(max_length=100, null=True, blank=True)  # 🏙️ Nouveau champ
    Client_telephone = models.CharField(max_length=20, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.Client_prenom} {self.Client_nom}"
    