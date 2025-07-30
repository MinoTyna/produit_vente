
from django.urls import path
from .views import SyncResponsableAPIView,ResponsableListAPIView,ResponsabletUpdateAPIView,ResponsableDetailView,ResponsableTotalAPIView

urlpatterns = [
    path('post', SyncResponsableAPIView.as_view(), name='sync_utilisateur'),
    path('get', ResponsableListAPIView.as_view(), name='liste_utilisateurs'),
    path('total', ResponsableTotalAPIView.as_view(), name='liste_utilisateurs'),
    path('get/<int:pk>', ResponsableDetailView.as_view(), name='liste_utilisateurs'),
    path('update/<int:responsable_id>', ResponsabletUpdateAPIView.as_view(), name='liste_utilisateurs'),
    # path('update-password/<int:pk>', UpdateResponsablePasswordView.as_view(), name='update-responsable-password'),

]
