from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Paiement, Achat
from dateutil.relativedelta import relativedelta
from responsable.models import Responsable
from .serializers import PaiementSerializer
from django.core.mail import EmailMessage
from .models import Paiement
from client.models import Client
from datetime import datetime, date, timedelta
from achats.models import Facture
from django.db.models import Max
from django.utils.timezone import now
from collections import defaultdict



def envoyer_sms(numero, message):
    # Simule l’envoi de SMS
    print(f"SMS envoyé à {numero} : {message}")


def envoyer_email(sujet, message, destinataires, reply_to=None):
    if not isinstance(destinataires, list):
        destinataires = [destinataires]

    email = EmailMessage(
        subject=sujet,
        body=message,
        from_email=None,  # utilisera DEFAULT_FROM_EMAIL de settings.py
        to=destinataires,
        reply_to=[reply_to] if reply_to else None
    )
    email.send(fail_silently=False)



# class PaiementCreateView(generics.CreateAPIView):
#     queryset = Paiement.objects.all()
#     serializer_class = PaiementSerializer

#     def create(self, request, *args, **kwargs):
#         client_id = request.data.get('client')
#         if not client_id:
#             return Response({"error": "Le champ 'client' est requis."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             montant_paye = Decimal(request.data.get('Paiement_montant', '0'))
#         except:
#             return Response({"error": "Le montant payé est invalide."}, status=status.HTTP_400_BAD_REQUEST)

#         if montant_paye < Decimal('100000'):
#             return Response({"error": "Le montant minimum à payer est de 100 000 Ariary."}, status=status.HTTP_400_BAD_REQUEST)

#         type_paiement = request.data.get('Paiement_type', '').lower()
#         if type_paiement not in ['comptant', 'mensuel']:
#             return Response({"error": "Type de paiement invalide."}, status=status.HTTP_400_BAD_REQUEST)

#         montant_choisi = None
#         date_choisie = None
#         prochaine_date = None

#         if type_paiement == 'mensuel':
#             dernier_paiement = Paiement.objects.filter(
#                 AchatsID__ClientID_id=client_id,
#                 Paiement_type='mensuel',
#                 Paiement_montantchoisi__isnull=False,
#                 Paiement_datechoisi__isnull=False
#             ).order_by('-Paiement_date').first()

#             if dernier_paiement:
#                 montant_choisi = dernier_paiement.Paiement_montantchoisi
#                 date_choisie = dernier_paiement.Paiement_datechoisi
#                 mois_a_ajouter = int(montant_paye / montant_choisi)
#                 prochaine_date = date_choisie + relativedelta(months=mois_a_ajouter)
#             else:
#                 montant_choisi_str = request.data.get('Paiement_montantchoisi')
#                 date_choisie_str = request.data.get('Paiement_datechoisi')

#                 if not montant_choisi_str or not date_choisie_str:
#                     return Response({
#                         "error": "Le montant choisi et la date choisie sont requis pour le premier paiement mensuel."
#                     }, status=status.HTTP_400_BAD_REQUEST)

#                 try:
#                     montant_choisi = Decimal(montant_choisi_str)
#                     date_choisie = datetime.strptime(date_choisie_str, "%Y-%m-%d").date()
#                 except:
#                     return Response({"error": "Montant ou date invalide (format attendu : YYYY-MM-DD)."},
#                                     status=status.HTTP_400_BAD_REQUEST)
#                 prochaine_date = date_choisie

#         achats_client = Achat.objects.filter(ClientID_id=client_id)
#         if not achats_client.exists():
#             return Response({"error": "Aucun achat trouvé pour ce client."}, status=status.HTTP_404_NOT_FOUND)

#         total_attendu = sum(achat.ProduitID.Produit_prix * achat.Achat_quantite for achat in achats_client)
#         total_deja_paye = Paiement.objects.filter(AchatsID__ClientID_id=client_id).aggregate(
#             total=Sum('Paiement_montant')
#         )['total'] or Decimal('0')

#         nouveau_total = total_deja_paye + montant_paye
#         reste = max(total_attendu - nouveau_total, Decimal('0'))
#         statut = "complet" if nouveau_total >= total_attendu else "incomplet"
#         montant_rendu = int(nouveau_total - total_attendu) if nouveau_total > total_attendu else 0

#         dernier_achat = achats_client.order_by('-Achat_date').first()

#         # 🔴 GÉNÉRATION DIRECTE DU NUMÉRO DE FACTURE ICI
#         today = now().date()
#         prefix = today.strftime("FACT-%Y%m%d-")
#         compteur = Facture.objects.filter(date_creation__date=today).count() + 1
#         numero_facture = f"{prefix}{compteur:04d}"

#         facture = Facture.objects.create(achat=dernier_achat, numero_facture=numero_facture)

#         data = request.data.copy()
#         data['AchatsID'] = dernier_achat.id
#         data['Paiement_montant'] = montant_paye

#         if type_paiement == 'mensuel':
#             data['Paiement_montantchoisi'] = montant_choisi
#             data['Paiement_datechoisi'] = prochaine_date
#         else:
#             data.pop('Paiement_montantchoisi', None)
#             data.pop('Paiement_datechoisi', None)

#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         paiement = serializer.save()

#         client = dernier_achat.ClientID
#         numero = client.Client_telephone

#         envoyer_sms(numero, f"Bonjour {client.Client_nom}, votre paiement de {montant_paye:.0f} Ar a été reçu. "
#                             f"Statut: {statut}. Reste à payer: {reste:.0f} Ar.")

#         responsable = dernier_achat.ResponsableID
#         vendeur_email = responsable.Responsable_email
#         admins = Responsable.objects.filter(Responsable_role='admin').values_list('Responsable_email', flat=True)
#         envoyer_email(
#             sujet=f"Confirmation de paiement - {client.Client_nom}",
#             message=(
#                 f"Le client {client.Client_nom} ({numero}) a effectué un paiement de {montant_paye:.0f} Ar.\n"
#                 f"Statut : {statut}\nReste à payer : {reste:.0f} Ar.\n"
#             ),
#             destinataires=list(admins) + [vendeur_email],
#             reply_to=vendeur_email
#         )

#         produits_achetes = [
#             {
#                 "nom": achat.ProduitID.Produit_nom,
#                 "quantite": achat.Achat_quantite,
#                 "prix_unitaire": int(achat.ProduitID.Produit_prix),
#                 "total": int(achat.ProduitID.Produit_prix * achat.Achat_quantite)
#             }
#             for achat in achats_client
#         ]

#         prixtotalproduit = sum(p["total"] for p in produits_achetes)
#         nombredemois_restant = int(reste / montant_choisi) if montant_choisi else None

#         return Response({
#             "repaiement": True if type_paiement == 'mensuel' and total_deja_paye > 0 else False,
#             "client": client.Client_nom,
#             "produits": produits_achetes,
#             "prixtotalproduit": prixtotalproduit,
#             "total_paye": int(nouveau_total),
#             "reste_a_payer": int(reste),
#             "montant_rendu": montant_rendu,
#             "statut": statut,
#             "Paiement_type": type_paiement,
#             "Paiement_montantchoisi": int(montant_choisi) if montant_choisi else None,
#             "nombredemois_restant": nombredemois_restant,
#             "date_paiement_prochaine": str(prochaine_date) if prochaine_date else None,
#             "numero_facture": facture.numero_facture,
#             "facture_id": facture.id,
#         }, status=status.HTTP_201_CREATED)




class PaiementCreateView(generics.CreateAPIView):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer

    def create(self, request, *args, **kwargs):
        client_id = request.data.get('client')
        if not client_id:
            return Response({"error": "Le champ 'client' est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            montant_paye = Decimal(request.data.get('Paiement_montant', '0'))
        except:
            return Response({"error": "Le montant payé est invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if montant_paye < Decimal('100000'):
            return Response({"error": "Le montant minimum à payer est de 100 000 Ariary."}, status=status.HTTP_400_BAD_REQUEST)

        type_paiement = request.data.get('Paiement_type', '').lower()
        if type_paiement not in ['comptant', 'mensuel']:
            return Response({"error": "Type de paiement invalide."}, status=status.HTTP_400_BAD_REQUEST)

        montant_choisi = None
        date_choisie = None
        prochaine_date = None

        if type_paiement == 'mensuel':
            dernier_paiement = Paiement.objects.filter(
                AchatsID__ClientID_id=client_id,
                Paiement_type='mensuel',
                Paiement_montantchoisi__isnull=False,
                Paiement_datechoisi__isnull=False
            ).order_by('-Paiement_date').first()

            if dernier_paiement:
                montant_choisi = dernier_paiement.Paiement_montantchoisi
                date_choisie = dernier_paiement.Paiement_datechoisi
                mois_a_ajouter = int(montant_paye / montant_choisi)
                prochaine_date = date_choisie + relativedelta(months=mois_a_ajouter)
            else:
                montant_choisi_str = request.data.get('Paiement_montantchoisi')
                date_choisie_str = request.data.get('Paiement_datechoisi')

                if not montant_choisi_str or not date_choisie_str:
                    return Response({
                        "error": "Le montant choisi et la date choisie sont requis pour le premier paiement mensuel."
                    }, status=status.HTTP_400_BAD_REQUEST)

                try:
                    montant_choisi = Decimal(montant_choisi_str)
                    date_choisie = datetime.strptime(date_choisie_str, "%Y-%m-%d").date()
                except:
                    return Response({"error": "Montant ou date invalide (format attendu : YYYY-MM-DD)."},
                                    status=status.HTTP_400_BAD_REQUEST)
                prochaine_date = date_choisie

        achats_client = Achat.objects.filter(ClientID_id=client_id)
        if not achats_client.exists():
            return Response({"error": "Aucun achat trouvé pour ce client."}, status=status.HTTP_404_NOT_FOUND)

        total_attendu = sum(achat.ProduitID.Produit_prix * achat.Achat_quantite for achat in achats_client)
        total_deja_paye = Paiement.objects.filter(AchatsID__ClientID_id=client_id).aggregate(
            total=Sum('Paiement_montant')
        )['total'] or Decimal('0')

        nouveau_total = total_deja_paye + montant_paye
        reste = max(total_attendu - nouveau_total, Decimal('0'))
        statut = "complet" if nouveau_total >= total_attendu else "incomplet"
        montant_rendu = int(nouveau_total - total_attendu) if nouveau_total > total_attendu else 0
        revenu = int(nouveau_total - total_attendu) if nouveau_total > total_attendu else 0

        dernier_achat = achats_client.order_by('-Achat_date').first()

        # Génération du numéro de facture
        # On cherche le dernier numéro de facture créé (le max des chiffres après "FACT-")
        last_facture = Facture.objects.order_by('-id').first()
        last_num = 0
        if last_facture and last_facture.numero_facture:
            import re
            match = re.search(r'FACT-(\d+)', last_facture.numero_facture)
            if match:
                last_num = int(match.group(1))
        new_num = last_num + 1
        numero_facture = f"FACT-{new_num:04d}"

        facture = Facture.objects.create(achat=dernier_achat, numero_facture=numero_facture)

        # Création du paiement
        data = request.data.copy()
        data['AchatsID'] = dernier_achat.id
        data['Paiement_montant'] = montant_paye

        if type_paiement == 'mensuel':
            data['Paiement_montantchoisi'] = montant_choisi
            data['Paiement_datechoisi'] = prochaine_date
        else:
            data.pop('Paiement_montantchoisi', None)
            data.pop('Paiement_datechoisi', None)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        paiement = serializer.save()

        # Envoi de SMS
        client = dernier_achat.ClientID
        numero = client.Client_telephone
        envoyer_sms(numero, f"Bonjour {client.Client_nom}, votre paiement de {montant_paye:.0f} Ar a été reçu. "
                            f"Statut: {statut}. Reste à payer: {reste:.0f} Ar.")

        # Envoi email aux admins et vendeur
        # responsable = dernier_achat.ResponsableID
        # vendeur_email = responsable.Responsable_email
        # admins = Responsable.objects.filter(Responsable_role='admin').values_list('Responsable_email', flat=True)
        # envoyer_email(
        #     sujet=f"Confirmation de paiement - {client.Client_nom}",
        #     message=(
        #         f"Le client {client.Client_nom} ({numero}) a effectué un paiement de {montant_paye:.0f} Ar.\n"
        #         f"Statut : {statut}\nReste à payer : {reste:.0f} Ar.\n"
        #         f"Revenu supplémentaire : {revenu:.0f} Ar.\n"
        #     ),
        #     destinataires=list(admins) + [vendeur_email],
        #     reply_to=vendeur_email
        # )

        produits_achetes = [
            {
                "nom": achat.ProduitID.Produit_nom,
                "quantite": achat.Achat_quantite,
                "prix_unitaire": int(achat.ProduitID.Produit_prix),
                "total": int(achat.ProduitID.Produit_prix * achat.Achat_quantite)
            }
            for achat in achats_client
        ]

        prixtotalproduit = sum(p["total"] for p in produits_achetes)
        nombredemois_restant = int(reste / montant_choisi) if montant_choisi else None

        return Response({
            "repaiement": True if type_paiement == 'mensuel' and total_deja_paye > 0 else False,
            "client": client.Client_nom,
            "produits": produits_achetes,
            "prixtotalproduit": prixtotalproduit,
            "total_paye": int(nouveau_total),
            "reste_a_payer": int(reste),
            "montant_rendu": montant_rendu,
            "revenu": revenu,
            "statut": statut,
            "Paiement_type": type_paiement,
            "Paiement_montantchoisi": int(montant_choisi) if montant_choisi else None,
            "nombredemois_restant": nombredemois_restant,
            "date_paiement_prochaine": str(prochaine_date) if prochaine_date else None,
            "numero_facture": facture.numero_facture,
            "facture_id": facture.id,
        }, status=status.HTTP_201_CREATED)

# class RepaiementCreateView(generics.CreateAPIView):
#     queryset = Paiement.objects.all()
#     serializer_class = PaiementSerializer

#     def create(self, request, *args, **kwargs):
#         client_id = request.data.get('client')
#         if not client_id:
#             return Response({"error": "Le champ 'client' est requis."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             montant_paye = Decimal(request.data.get('Paiement_montant', '0'))
#         except:
#             return Response({"error": "Le montant payé est invalide."}, status=status.HTTP_400_BAD_REQUEST)

#         if montant_paye < Decimal('100000'):
#             return Response({"error": "Le montant minimum à payer est de 100 000 Ariary."},
#                             status=status.HTTP_400_BAD_REQUEST)

#         type_paiement = request.data.get('Paiement_type', '').lower()
#         if type_paiement not in ['comptant', 'mensuel']:
#             return Response({"error": "Type de paiement invalide."}, status=status.HTTP_400_BAD_REQUEST)

#         montant_choisi = None
#         date_choisie = None
#         prochaine_date = None

#         if type_paiement == 'mensuel':
#             dernier_paiement = Paiement.objects.filter(
#                 AchatsID__ClientID_id=client_id,
#                 Paiement_type='mensuel',
#                 Paiement_montantchoisi__isnull=False,
#                 Paiement_datechoisi__isnull=False
#             ).order_by('-Paiement_date').first()

#             if dernier_paiement:
#                 montant_choisi = dernier_paiement.Paiement_montantchoisi
#                 date_choisie = dernier_paiement.Paiement_datechoisi
#                 mois_a_ajouter = int(montant_paye / montant_choisi)
#                 prochaine_date = date_choisie + relativedelta(months=mois_a_ajouter)
#             else:
#                 montant_choisi_str = request.data.get('Paiement_montantchoisi')
#                 date_choisie_str = request.data.get('Paiement_datechoisi')

#                 if not montant_choisi_str or not date_choisie_str:
#                     return Response({
#                         "error": "Le montant choisi et la date choisie sont requis pour le premier paiement mensuel."
#                     }, status=status.HTTP_400_BAD_REQUEST)

#                 try:
#                     montant_choisi = Decimal(montant_choisi_str)
#                     date_choisie = datetime.strptime(date_choisie_str, "%Y-%m-%d").date()
#                 except:
#                     return Response({"error": "Montant ou date invalide (format attendu : YYYY-MM-DD)."},
#                                     status=status.HTTP_400_BAD_REQUEST)
#                 prochaine_date = date_choisie  # premier paiement → date choisie d'origine

#         achats_client = Achat.objects.filter(ClientID_id=client_id)
#         if not achats_client.exists():
#             return Response({"error": "Aucun achat trouvé pour ce client."}, status=status.HTTP_404_NOT_FOUND)

#         total_attendu = sum(achat.ProduitID.Produit_prix * achat.Achat_quantite for achat in achats_client)
#         total_deja_paye = Paiement.objects.filter(AchatsID__ClientID_id=client_id).aggregate(
#             total=Sum('Paiement_montant')
#         )['total'] or Decimal('0')

#         nouveau_total = total_deja_paye + montant_paye
#         reste = max(total_attendu - nouveau_total, Decimal('0'))
#         statut = "complet" if nouveau_total >= total_attendu else "incomplet"
#         montant_rendu = int(nouveau_total - total_attendu) if nouveau_total > total_attendu else 0

#         dernier_achat = achats_client.order_by('-Achat_date').first()

#         # Construction des données à enregistrer
#         data = request.data.copy()
#         data['AchatsID'] = dernier_achat.id
#         data['Paiement_montant'] = montant_paye

#         if type_paiement == 'mensuel':
#             data['Paiement_montantchoisi'] = montant_choisi
#             data['Paiement_datechoisi'] = prochaine_date
#         else:
#             data.pop('Paiement_montantchoisi', None)
#             data.pop('Paiement_datechoisi', None)

#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         paiement = serializer.save()

#         # Création de la facture liée à cet achat (si pas déjà créée)
#         facture_existante = Facture.objects.filter(achat=dernier_achat).exists()
#         if not facture_existante:
#             facture = Facture.objects.create(achat=dernier_achat)
#         else:
#             facture = Facture.objects.get(achat=dernier_achat)

#         # SMS
#         client = dernier_achat.ClientID
#         # numero = client.Client_telephone
#         prenom = client.Client_prenom
#         # envoyer_sms(numero, f"Bonjour {client.Client_nom}, votre paiement de {montant_paye:.0f} Ar a été reçu. "
#         #                     f"Statut: {statut}. Reste à payer: {reste:.0f} Ar.")

#         # Mail
#         responsable = dernier_achat.ResponsableID
#         vendeur_email = responsable.Responsable_email
#         admins = Responsable.objects.filter(Responsable_role='admin').values_list('Responsable_email', flat=True)
#         envoyer_email(
#             sujet=f"Confirmation de paiement - {client.Client_nom}",
#             message=(
#                 f"Le client {client.Client_nom} ({prenom}) a effectué un paiement de {montant_paye:.0f} Ar.\n"
#                 f"Statut : {statut}\nReste à payer : {reste:.0f} Ar.\n"
#             ),
#             destinataires=list(admins) + [vendeur_email],
#             reply_to=vendeur_email
#         )

#         # Produits
#         produits_achetes = [
#             {
#                 "nom": achat.ProduitID.Produit_nom,
#                 "quantite": achat.Achat_quantite,
#                 "prix_unitaire": int(achat.ProduitID.Produit_prix),
#                 "total": int(achat.ProduitID.Produit_prix * achat.Achat_quantite)
#             }
#             for achat in achats_client
#         ]
#         prixtotalproduit = sum(p["total"] for p in produits_achetes)

#         nombredemois_restant = int(reste / montant_choisi) if montant_choisi else None

#         return Response({
#             "repaiement": True if type_paiement == 'mensuel' and total_deja_paye > 0 else False,
#             "client": client.Client_nom,
#             "produits": produits_achetes,
#             "prixtotalproduit": prixtotalproduit,
#             "total_paye": int(nouveau_total),
#             "reste_a_payer": int(reste),
#             "montant_rendu": montant_rendu,
#             "statut": statut,
#             "Paiement_type": type_paiement,
#             "Paiement_montantchoisi": int(montant_choisi) if montant_choisi else None,
#             "nombredemois_restant": nombredemois_restant,
#             "date_paiement_prochaine": str(prochaine_date) if prochaine_date else None,
#             "numero_facture": facture.numero_facture,
#             "facture_id": facture.id,
#         }, status=status.HTTP_201_CREATED)


class RepaiementCreateView(generics.CreateAPIView):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer

    def create(self, request, *args, **kwargs):
        client_id = request.data.get('client')
        if not client_id:
            return Response({"error": "Le champ 'client' est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            montant_paye = Decimal(request.data.get('Paiement_montant', '0'))
        except:
            return Response({"error": "Le montant payé est invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if montant_paye < Decimal('100000'):
            return Response({"error": "Le montant minimum à payer est de 100 000 Ariary."},
                            status=status.HTTP_400_BAD_REQUEST)

        type_paiement = request.data.get('Paiement_type', '').lower()
        if type_paiement not in ['comptant', 'mensuel']:
            return Response({"error": "Type de paiement invalide."}, status=status.HTTP_400_BAD_REQUEST)

        montant_choisi = None
        date_choisie = None
        prochaine_date = None

        if type_paiement == 'mensuel':
            dernier_paiement = Paiement.objects.filter(
                AchatsID__ClientID_id=client_id,
                Paiement_type='mensuel',
                Paiement_montantchoisi__isnull=False,
                Paiement_datechoisi__isnull=False
            ).order_by('-Paiement_date').first()

            if dernier_paiement:
                montant_choisi = dernier_paiement.Paiement_montantchoisi
                date_choisie = dernier_paiement.Paiement_datechoisi
                mois_a_ajouter = int(montant_paye / montant_choisi)
                prochaine_date = date_choisie + relativedelta(months=mois_a_ajouter)
            else:
                montant_choisi_str = request.data.get('Paiement_montantchoisi')
                date_choisie_str = request.data.get('Paiement_datechoisi')

                if not montant_choisi_str or not date_choisie_str:
                    return Response({
                        "error": "Le montant choisi et la date choisie sont requis pour le premier paiement mensuel."
                    }, status=status.HTTP_400_BAD_REQUEST)

                try:
                    montant_choisi = Decimal(montant_choisi_str)
                    date_choisie = datetime.strptime(date_choisie_str, "%Y-%m-%d").date()
                except:
                    return Response({"error": "Montant ou date invalide (format attendu : YYYY-MM-DD)."},
                                    status=status.HTTP_400_BAD_REQUEST)
                prochaine_date = date_choisie

        achats_client = Achat.objects.filter(ClientID_id=client_id)
        if not achats_client.exists():
            return Response({"error": "Aucun achat trouvé pour ce client."}, status=status.HTTP_404_NOT_FOUND)

        total_attendu = sum(achat.ProduitID.Produit_prix * achat.Achat_quantite for achat in achats_client)
        total_deja_paye = Paiement.objects.filter(AchatsID__ClientID_id=client_id).aggregate(
            total=Sum('Paiement_montant')
        )['total'] or Decimal('0')

        nouveau_total = total_deja_paye + montant_paye
        reste = max(total_attendu - nouveau_total, Decimal('0'))
        statut = "complet" if nouveau_total >= total_attendu else "incomplet"
        montant_rendu = int(nouveau_total - total_attendu) if nouveau_total > total_attendu else 0

        dernier_achat = achats_client.order_by('-Achat_date').first()

        data = request.data.copy()
        data['AchatsID'] = dernier_achat.id
        data['Paiement_montant'] = montant_paye

        if type_paiement == 'mensuel':
            data['Paiement_montantchoisi'] = montant_choisi
            data['Paiement_datechoisi'] = prochaine_date
        else:
            data.pop('Paiement_montantchoisi', None)
            data.pop('Paiement_datechoisi', None)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        paiement = serializer.save()

        # Création de facture si absente
        facture, _ = Facture.objects.get_or_create(achat=dernier_achat)

        client = dernier_achat.ClientID
        prenom = client.Client_prenom

        responsable = dernier_achat.ResponsableID
        vendeur_email = responsable.Responsable_email
        admins = Responsable.objects.filter(Responsable_role='admin').values_list('Responsable_email', flat=True)
        envoyer_email(
            sujet=f"Confirmation de paiement - {client.Client_nom}",
            message=(
                f"Le client {client.Client_nom} ({prenom}) a effectué un paiement de {montant_paye:.0f} Ar.\n"
                f"Statut : {statut}\nReste à payer : {reste:.0f} Ar.\n"
            ),
            destinataires=list(admins) + [vendeur_email],
            reply_to=vendeur_email
        )

        produits_achetes = [
            {
                "nom": achat.ProduitID.Produit_nom,
                "quantite": achat.Achat_quantite,
                "prix_unitaire": int(achat.ProduitID.Produit_prix),
                "total": int(achat.ProduitID.Produit_prix * achat.Achat_quantite)
            }
            for achat in achats_client
        ]
        prixtotalproduit = sum(p["total"] for p in produits_achetes)
        nombredemois_restant = int(reste / montant_choisi) if montant_choisi else None

        # ✅ Calcul du revenu total encaissé pour ce client
        revenu_total = Paiement.objects.filter(AchatsID__ClientID_id=client_id).aggregate(
            revenu=Sum('Paiement_montant')
        )['revenu'] or Decimal('0')

        return Response({
            "repaiement": True if type_paiement == 'mensuel' and total_deja_paye > 0 else False,
            "client": client.Client_nom,
            "produits": produits_achetes,
            "prixtotalproduit": prixtotalproduit,
            "total_paye": int(nouveau_total),
            "reste_a_payer": int(reste),
            "montant_rendu": montant_rendu,
            "statut": statut,
            "Paiement_type": type_paiement,
            "Paiement_montantchoisi": int(montant_choisi) if montant_choisi else None,
            "nombredemois_restant": nombredemois_restant,
            "date_paiement_prochaine": str(prochaine_date) if prochaine_date else None,
            "numero_facture": facture.numero_facture,
            "facture_id": facture.id,
            "revenu": int(montant_paye),         # ✅ Revenu généré par ce paiement
            "revenu_total": int(revenu_total),   # ✅ Revenu total payé par ce client
        }, status=status.HTTP_201_CREATED)

class PaiementListView(generics.ListAPIView):
    queryset = Paiement.objects.all().order_by('-Paiement_date')
    serializer_class = PaiementSerializer 


class ListeResteAPayerParClient(APIView):
    def get(self, request):
        data_par_datetime = defaultdict(list)
        clients = Client.objects.all()

        for client in clients:
            achats = Achat.objects.filter(ClientID=client)
            if not achats.exists():
                continue

            # ✅ Grouper les achats du client par datetime complet
            achats_par_datetime = defaultdict(list)
            for achat in achats:
                datetime_key = achat.Achat_date.strftime("%Y-%m-%d %H:%M:%S")
                achats_par_datetime[datetime_key].append(achat)

            for datetime_str, achats_group in achats_par_datetime.items():
                produits_achetes = []
                total_attendu = Decimal('0')

                for achat in achats_group:
                    produit = achat.ProduitID
                    quantite = achat.Achat_quantite
                    prix_unitaire = Decimal(produit.Produit_prix)
                    total = prix_unitaire * quantite
                    total_attendu += total

                    produits_achetes.append({
                        "nom": produit.Produit_nom,
                        "quantite": quantite,
                        "prix_unitaire": int(prix_unitaire),
                        "total": int(total)
                    })

                paiements_client = Paiement.objects.filter(AchatsID__ClientID=client)
                total_paye = paiements_client.aggregate(total=Sum('Paiement_montant'))['total'] or Decimal('0')
                reste = max(total_attendu - total_paye, Decimal('0'))
                statut = "complet" if total_paye >= total_attendu else "incomplet"

                paiements_mensuels = paiements_client.filter(Paiement_type='mensuel')
                prochaine_date = paiements_mensuels.aggregate(max_date=Max("Paiement_datechoisi"))['max_date']
                montant_choisi = paiements_mensuels.last().Paiement_montantchoisi if paiements_mensuels.exists() else None
                nombredemois_restant = int(reste / montant_choisi) if montant_choisi and montant_choisi > 0 else None
                progress = int((total_paye / total_attendu) * 100) if total_attendu > 0 else 0

                data_par_datetime[datetime_str].append({
                    "id": client.id,
                    "client": client.Client_nom,
                    "prenom": client.Client_prenom,
                    "achats_par_date": [
                        {
                            "date": datetime_str,
                            "produits": produits_achetes
                        }
                    ],
                    "prixtotalproduit": int(total_attendu),
                    "total_paye": int(total_paye),
                    "reste_a_payer": int(reste),
                    "statut": statut,
                    "progress": progress,
                    "date_paiement_prochaine": str(prochaine_date) if prochaine_date else None,
                    "nombredemois_restant": nombredemois_restant,
                })

        # ✅ Conversion vers une liste finale
        response_data = []
        for datetime_str, clients_list in data_par_datetime.items():
            response_data.append({
                "date": datetime_str,
                "clients": clients_list
            })

        return Response(response_data, status=status.HTTP_200_OK)



class VerifierPaiementListView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        date_debut = date.today()
        paiements = Paiement.objects.all()
        notifications = []

        for paiement in paiements:
            date_utilisee = paiement.Paiement_datechoisi
            if not date_utilisee:
                continue

            seuil = date_utilisee - date_debut

            if timedelta(days=0) <= seuil <= timedelta(days=5):
                achat = paiement.AchatsID
                client = achat.ClientID
                responsable = achat.ResponsableID

                message = (
                    f"⚠️ Le client {client.Client_nom} "
                    f"doit payer le deuxième paiement le {paiement.Paiement_datechoisi} "
                    f"(achat effectué le {achat.Achat_date})."
                )

                notifications.append({
                    "message": message,
                    "client_id": client.id,
                    "achat_date": achat.Achat_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "date_paiement": str(paiement.Paiement_datechoisi),
                })

                # if responsable and responsable.Responsable_email:
                #     envoyer_email(
                #         sujet="Paiement proche à effectuer",
                #         message=message,
                #         destinataires=responsable.Responsable_email
                #     )

        return Response({"messages": notifications}, status=status.HTTP_200_OK)


from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware


class ListePayerParClient(APIView):
    def get(self, request, client_id, date_achat):
        client = get_object_or_404(Client, id=client_id)

        try:
            date_dt = datetime.fromisoformat(date_achat)
            date_dt = make_aware(date_dt)
        except ValueError:
            return Response({"detail": "Format de date invalide."}, status=400)

        date_debut = date_dt.replace(second=0, microsecond=0)
        date_fin = date_debut + timedelta(minutes=1)

        achats = Achat.objects.filter(
            ClientID=client,
            Achat_date__gte=date_debut,
            Achat_date__lt=date_fin,
        )

        if not achats.exists():
            return Response({"detail": "Aucun achat trouvé pour ce client à cette date."}, status=404)

        paiements = Paiement.objects.filter(AchatsID__in=achats).order_by('Paiement_date')
        total_paye = paiements.aggregate(total=Sum('Paiement_montant'))['total'] or Decimal('0.0')
        # total_paye = paiements.aggregate(total=Sum('Paiement_montant'))['total'] or Decimal('0')


        # Construire les données des produits
        produits = []
        for achat in achats:
            produit = achat.ProduitID
            prix_unitaire = float(produit.Produit_prix)  # ⚠️ adapte le nom exact du champ prix si différent
            quantite = achat.Achat_quantite
            total = prix_unitaire * quantite
            produits.append({
                "nom": produit.Produit_nom,
                "quantite": quantite,
                "prix_unitaire": prix_unitaire,
                "total": total
            })

        # Total des produits
        prixtotalproduit = sum(p["total"] for p in produits)

        # Calcul du reste à payer
        reste = float(prixtotalproduit) - float(total_paye)
        statut = "complet" if reste <= 0 else "incomplet"


        
        paiements_mensuels = paiements.filter(Paiement_type='mensuel')
        prochaine_date = paiements_mensuels.aggregate(max_date=Max("Paiement_datechoisi"))['max_date']
        montant_choisi = paiements_mensuels.last().Paiement_montantchoisi if paiements_mensuels.exists() else None

        # Conversion en float pour éviter le conflit float / Decimal
        nombredemois_restant = int(reste / float(montant_choisi)) if montant_choisi and montant_choisi > 0 else None

        paiements_data = [
            {
                "id": p.id,
                "montant": float(p.Paiement_montant),
                "date": p.Paiement_date.isoformat(),
                "responsable": p.AchatsID.ResponsableID.Responsable_email,
            }
            for p in paiements
        ]

        return Response({
            "client": {
                "photo": client.Client_photo.url if client.Client_photo else None,
                "nom": client.Client_nom,
                "prenom": client.Client_prenom,
                "telephone": client.Client_telephone,
                "adresse": client.Client_adresse,
                "cin": client.Client_cin,
            },
            "date_achat": date_dt.isoformat(),
            "produits": produits,
            "paiements": paiements_data,
            "prixtotalproduit": prixtotalproduit,
            "total_paye": float(total_paye),
            "reste_a_payer": reste,
            "statut": statut,
            "date_paiement_prochaine": str(prochaine_date) if prochaine_date else None,
            "nombredemois_restant": nombredemois_restant,
      
        })

class SmsVerifierByClientView(APIView):
    def get(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({"error": "Client non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        paiements = Paiement.objects.filter(AchatsID__ClientID=client)

        today = date.today()
        notifications = []

        for paiement in paiements:
            date_choisi = paiement.Paiement_datechoisi
            if not date_choisi:
                continue

            delta = date_choisi - today

            if timedelta(days=0) <= delta <= timedelta(days=5):
                message = (
                    f"⚠️ Bonjour {client.Client_nom}, votre prochain paiement est prévu le "
                    f"{date_choisi.strftime('%d/%m/%Y')}."
                )
                try:
                    if client.Client_telephone:
                        envoyer_sms(client.Client_telephone, message)
                        notifications.append({"message": message, "paiement_id": paiement.id})
                except Exception as e:
                    notifications.append({"error": str(e), "paiement_id": paiement.id})

        if not notifications:
            return Response({"info": "Aucun paiement proche à notifier."})

        return Response({"notifications": notifications})

class PaiementDeleteAPIView(APIView):
    def delete(self, request, paiement_id, format=None):
        try:
            paiement = Paiement.objects.get(pk=paiement_id)
        except Paiement.DoesNotExist:
            return Response({"error": "Paiement non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        achat = paiement.AchatsID
        client = achat.ClientID

        # Sauvegarder le montant du paiement avant suppression
        montant_supprime = paiement.Paiement_montant

        # Supprimer le paiement
        paiement.delete()

        # Recalculer le total payé après suppression
        total_paye = achat.paiements_details.aggregate(
            total=Sum('Paiement_montant')
        )['total'] or Decimal('0')

        total_attendu = achat.ProduitID.Produit_prix * achat.Achat_quantite
        reste = max(total_attendu - total_paye, Decimal('0'))
        statut = "complet" if total_paye >= total_attendu else "incomplet"

        return Response({
            "message": "Paiement supprimé avec succès.",
            "client": client.Client_nom,
            "produit": achat.ProduitID.Produit_nom,
            "quantite": achat.Achat_quantite,
            "total_attendu": float(total_attendu),
            "total_paye": float(total_paye),
            "reste_a_payer": float(reste),
            "statut": statut,
            "montant_supprime": float(montant_supprime),
        }, status=status.HTTP_200_OK)



class PaiementUpdateView(generics.UpdateAPIView):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer

    def update(self, request, *args, **kwargs):
        paiement = self.get_object()
        client_id = request.data.get('client')

        if not client_id:
            return Response({"error": "Le champ 'client' est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            montant_paye = Decimal(request.data.get('Paiement_montant', paiement.Paiement_montant))
        except:
            return Response({"error": "Le montant payé est invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if montant_paye < Decimal('100000'):
            return Response({"error": "Le montant minimum à payer est de 100 000 Ariary."},
                            status=status.HTTP_400_BAD_REQUEST)

        type_paiement = request.data.get('Paiement_type', paiement.Paiement_type).lower()
        if type_paiement not in ['comptant', 'mensuel']:
            return Response({"error": "Type de paiement invalide."}, status=status.HTTP_400_BAD_REQUEST)

        montant_choisi = None
        date_choisie = None
        prochaine_date = None

        if type_paiement == 'mensuel':
            montant_choisi_str = request.data.get('Paiement_montantchoisi')
            date_choisie_str = request.data.get('Paiement_datechoisi')

            if not date_choisie_str:
                return Response({
                    "error": "La date choisie est requise pour un paiement mensuel."
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                date_choisie = datetime.strptime(str(date_choisie_str), "%Y-%m-%d").date()
                prochaine_date = date_choisie
            except:
                return Response({"error": "Date invalide (format attendu : YYYY-MM-DD)."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Conserver le montant existant si non fourni
            try:
                montant_choisi = Decimal(montant_choisi_str) if montant_choisi_str else paiement.Paiement_montantchoisi
            except:
                return Response({"error": "Montant mensuel invalide."}, status=status.HTTP_400_BAD_REQUEST)

        else:
            request.data.pop('Paiement_montantchoisi', None)
            request.data.pop('Paiement_datechoisi', None)

        achats_client = Achat.objects.filter(ClientID_id=client_id)
        if not achats_client.exists():
            return Response({"error": "Aucun achat trouvé pour ce client."}, status=status.HTTP_404_NOT_FOUND)

        dernier_achat = achats_client.order_by('-Achat_date').first()

        data = request.data.copy()
        data['AchatsID'] = dernier_achat.id
        data['Paiement_montant'] = montant_paye

        if type_paiement == 'mensuel':
            data['Paiement_montantchoisi'] = montant_choisi
            data['Paiement_datechoisi'] = prochaine_date

        serializer = self.get_serializer(paiement, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        total_attendu = sum(achat.ProduitID.Produit_prix * achat.Achat_quantite for achat in achats_client)
        total_deja_paye = Paiement.objects.filter(AchatsID__ClientID_id=client_id).aggregate(
            total=Sum('Paiement_montant')
        )['total'] or Decimal('0')

        nouveau_total = total_deja_paye
        reste = max(total_attendu - nouveau_total, Decimal('0'))
        statut = "complet" if nouveau_total >= total_attendu else "incomplet"
        montant_rendu = int(nouveau_total - total_attendu) if nouveau_total > total_attendu else 0

        client = dernier_achat.ClientID
        numero = client.Client_telephone

        # Notification SMS
        envoyer_sms(numero, f"Bonjour {client.Client_nom}, votre paiement de {montant_paye:.0f} Ar a été mis à jour. "
                            f"Statut: {statut}. Reste à payer: {reste:.0f} Ar.")

        # # Email aux responsables
        # responsable = dernier_achat.ResponsableID
        # vendeur_email = responsable.Responsable_email
        # admins = Responsable.objects.filter(Responsable_role='admin').values_list('Responsable_email', flat=True)

        # Optionnel : Décommente pour activer l'email
        # envoyer_email(
        #     sujet=f"Mise à jour du paiement - {client.Client_nom}",
        #     message=(f"Le client {client.Client_nom} ({numero}) a modifié un paiement de {montant_paye:.0f} Ar.\n"
        #              f"Statut : {statut}\nReste à payer : {reste:.0f} Ar.\n"),
        #     destinataires=list(admins) + [vendeur_email],
        #     reply_to=vendeur_email
        # )

        produits_achetes = [
            {
                "nom": achat.ProduitID.Produit_nom,
                "quantite": achat.Achat_quantite,
                "prix_unitaire": int(achat.ProduitID.Produit_prix),
                "total": int(achat.ProduitID.Produit_prix * achat.Achat_quantite)
            }
            for achat in achats_client
        ]

        prixtotalproduit = sum(p["total"] for p in produits_achetes)
        nombredemois_restant = int(reste / montant_choisi) if montant_choisi else None

        return Response({
            "client": {
                "nom": client.Client_nom,
                "telephone": client.Client_telephone,
                "adresse": client.Client_adresse,
                "cin": client.Client_cin,
            },
            "produits": produits_achetes,
            "prixtotalproduit": prixtotalproduit,
            "total_paye": int(nouveau_total),
            "reste_a_payer": int(reste),
            "montant_rendu": montant_rendu,
            "statut": statut,
            "Paiement_type": type_paiement,
            "Paiement_montantchoisi": int(montant_choisi) if montant_choisi else None,
            "nombredemois_restant": nombredemois_restant,
            "date_paiement_prochaine": str(prochaine_date) if prochaine_date else None
        }, status=status.HTTP_200_OK)



from django.db.models import F, Sum, ExpressionWrapper, DecimalField
class ChiffreAffairesAPIView(APIView):
    def get(self, request):
        # 1. Chiffre d'affaires réel (paiements enregistrés)
        total_ca = Paiement.objects.aggregate(
            total=Sum('Paiement_montant')
        )['total'] or 0

        # 2. Total attendu : quantité * prix produit
        achats = Achat.objects.annotate(
            total=ExpressionWrapper(
                F('Achat_quantite') * F('ProduitID__Produit_prix'),
                output_field=DecimalField()
            )
        )

        total_attendu = sum([a.total for a in achats])

        # 3. Différence (reste dû)
        montant_restant = total_attendu - total_ca

        return Response({
            "chiffre_affaires": float(total_ca),
            "montant_total_attendu": float(total_attendu),
            "montant_restant_du": float(montant_restant) if montant_restant > 0 else 0.0
        })
class PaiementView(APIView):
    def get(self, request):
        mois = request.query_params.get('mois')
        annee = request.query_params.get('annee')

        paiements = Paiement.objects.all()

        if mois and annee:
            paiements = paiements.filter(Paiement_date__month=mois, Paiement_date__year=annee)
        elif mois:
            paiements = paiements.filter(Paiement_date__month=mois)
        elif annee:
            paiements = paiements.filter(Paiement_date__year=annee)

        paiements = paiements.order_by('Paiement_date')

        resultats = []

        total_paye_map = {}  # Pour cumuler les paiements par achat

        for paiement in paiements:
            achat = paiement.AchatsID
            client = achat.ClientID
            responsable = achat.ResponsableID
            facture = Facture.objects.filter(achat=achat).first()

            key_achat = achat.id
            if key_achat not in total_paye_map:
                total_paye_map[key_achat] = Decimal('0')
            total_paye_map[key_achat] += paiement.Paiement_montant

            total_attendu = achat.ProduitID.Produit_prix * achat.Achat_quantite
            total_paye = total_paye_map[key_achat]
            reste_a_payer = max(total_attendu - total_paye, Decimal('0'))
            statut = "complet" if total_paye >= total_attendu else "incomplet"

            produits = [{
                "nom": achat.ProduitID.Produit_nom,
                "quantite": achat.Achat_quantite,
                "prix_unitaire": int(achat.ProduitID.Produit_prix),
                "total": int(total_attendu)
            }]

            resultats.append({
                "paiement": {
                    "id": paiement.id,
                    "AchatsID": achat.id,
                    "Paiement_montant": str(paiement.Paiement_montant)
                },
                "facture_id": facture.id if facture else None,
                "numero_facture": facture.numero_facture if facture else None,
                "date_creation": facture.date_creation if facture else None,
                "client": client.Client_nom,
                "telephone": client.Client_telephone,
                "responsable": {
                    "id": responsable.id,
                    "nom": responsable.Responsable_nom,
                    "telephone_res": responsable.Responsable_telephone
                },
                "produits": produits,
                "prixtotalproduit": int(total_attendu),
                "total_paye": int(total_paye),
                "reste_a_payer": int(reste_a_payer),
                "statut": statut
            })

        return Response(resultats, status=status.HTTP_200_OK)

