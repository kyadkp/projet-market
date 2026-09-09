import os
import django
import openpyxl
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionmarche.settings')
django.setup()

from gestion.models import Client, Cantine  

FICHIERS = {
    'A': 'BLOC A.xlsx',
    'B': 'BLOC B.xlsx',
    'C': 'BLOC C.xlsx',
    'D': 'BLOC D.xlsx',
}

IGNORÉS = ['march amb', 'a voir', '?', '', None]

def nettoyer_prix(valeur):
    if valeur is None:
        return 0
    try:
        return int(str(valeur).replace(' ', '').replace('\xa0', ''))
    except:
        return 0

def est_vacant(nom):
    if nom is None:
        return True
    return str(nom).strip().lower() in IGNORÉS or str(nom).strip().startswith('?')

def importer_bloc(bloc, fichier):
    print(f"\n📦 Import {bloc} depuis {fichier}...")
    wb = openpyxl.load_workbook(fichier, data_only=True)
    ws = wb.active

    for row in ws.iter_rows(min_row=2, values_only=True):  # min_row=2 pour sauter l'en-tête
        numero, proprietaire, surface, prix, *reste = row

        if not numero:
            continue

        numero = str(numero).strip()
        prix = nettoyer_prix(prix)
        surface = str(surface).strip() if surface else ''
        notes = str(reste[0]).strip() if reste and reste[0] else ''
        vacant = est_vacant(proprietaire)

        client = None
        if not vacant:
            nom = str(proprietaire).strip()
            client, _ = Client.objects.get_or_create(
                nom=nom,
                defaults={'telephone': ''}
            )

        cantine, created = Cantine.objects.update_or_create(
            matricule=numero,
            defaults={
                'client': client,
                'superficie': surface,
                'montant_a_payer': prix,
                'bloc': bloc,
                'notes': notes,
                'est_vacant': vacant,
            }
        )

        statut = '✅ créé' if created else '🔄 mis à jour'
        print(f"  {statut} : {numero} — {proprietaire}")

for bloc, fichier in FICHIERS.items():
    if os.path.exists(fichier):
        importer_bloc(bloc, fichier)
    else:
        print(f"⚠️  Fichier introuvable : {fichier}")

print("\n✅ Import terminé.")