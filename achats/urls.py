from django.urls import path
from .views import EnregistrerAchatAPIView, ListAchatAPIView, AchatDeleteAPIView,AchatListAPIView,FactureHistoriqueView,FactureAllView,TotalAchatsParResponsableAPIView,ProduitSortieTotalAPIView,ProduitPlusVenduAPIView,FactureDate,PaiementListView,ProduitsParResponsableAPIView,StatistiquesResponsableAPIView,ClientsFidelesAPIView,ProduitSortieTotalAPI,StatistiquesResponsableAPI

urlpatterns = [
    path('post', EnregistrerAchatAPIView.as_view(), name='enregistrer-achats'),
    path('get/<int:client_id>', ListAchatAPIView.as_view(), name='liste-achats'),
    path('get', AchatListAPIView.as_view(), name='liste-achats'),
    path('statique', StatistiquesResponsableAPIView.as_view(), name='liste-achats'),
    path('global', StatistiquesResponsableAPI.as_view(), name='liste-achats'),
    path('client', ClientsFidelesAPIView.as_view(), name='liste-achats'),
    path('sortie', ProduitSortieTotalAPIView.as_view(), name='sortie-achats'),
    path('sorti', ProduitSortieTotalAPI.as_view(), name='sortie-achats'),
    path('produit/vendu', ProduitPlusVenduAPIView.as_view(), name='vendu-achats'),
    path('facture/<int:pk>', FactureHistoriqueView.as_view(), name='facture-achats'),
    path('total/<int:responsable_id>', TotalAchatsParResponsableAPIView.as_view(), name='facture-achats'),
    path('facture', FactureAllView.as_view(), name='facture'),
    path('paiement', PaiementListView.as_view(), name='paiement'),
    path('factures', FactureDate.as_view(), name='facture'),
    path('delete/<int:achat_id>', AchatDeleteAPIView.as_view(), name='liste-achats'),
]
