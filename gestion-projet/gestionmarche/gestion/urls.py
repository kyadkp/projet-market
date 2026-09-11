from django.urls import path
from . import views


urlpatterns = [
    path('', views.login_view, name='login'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('clients/', views.clients_list, name='clients_list'),

    path('clients/add-full/', views.client_full_create, name='client_full_create'),

    path('clients/<int:id>/', views.client_detail, name='client_detail'),

    # Modification des informations du client
    path(
        'clients/<int:id>/edit/',
        views.client_update,
        name='client_update'
    ),

     path(
        'clients/<int:id>/cantines/add/',
        views.cantine_create_for_client,
        name='cantine_create_for_client'
        ),

    # Modification d'une cantine précise
    path(
        'cantines/<int:id>/edit/',
        views.cantine_update,
        name='cantine_update'
    ),
   

    # Ajout d'un versement à une cantine précise
    path(
        'cantines/<int:id>/paiement/add/',
        views.paiement_add,
        name='paiement_add'
    ),

    path(
    'paiements/<int:id>/edit/',
    views.paiement_update,
    name='paiement_update'
),

path(
    'paiements/<int:id>/delete/',
    views.paiement_delete,
    name='paiement_delete'
),

    path('clients/<int:id>/delete/', views.client_delete, name='client_delete'),

    path('cantines/', views.cantines_list, name='cantines_list'),

    path('paiements/', views.paiements_list, name='paiements_list'),
]