from django.contrib import admin
from .models import Client, Cantine, Paiement

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'telephone']
    search_fields = ['nom']


@admin.register(Cantine)
class CantineAdmin(admin.ModelAdmin):
    list_display = ['numero_cantine',  'client', 'superficie']
    search_fields = ['numero_cantine', 'client__nom']
    list_filter = ['superficie']


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['cantine', 'montant_paye', 'date_paiement']
    list_filter = ['date_paiement']