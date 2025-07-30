from django.db import models
from django.core.validators import MinValueValidator

class Produit(models.Model):
    Produit_nom = models.CharField(max_length=40)
    Produit_description = models.TextField(blank=True, null=True)
    Produit_reference = models.TextField(blank=True, null=True)
    Produit_prix = models.IntegerField() 
    Produit_photo = models.ImageField(upload_to='produits/photos/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
  
    Produit_quantite = models.PositiveIntegerField(
        null=True,               
        blank=True,              
        validators=[MinValueValidator(0)]  
    )

    def __str__(self):
        return self.nom
