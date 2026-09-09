from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('clients/', views.clients_list, name='clients_list'),
    # path('clients/add/', views.client_create, name='client_create'),
    path('cantines/', views.cantines_list, name='cantines_list'),
    path('paiements/', views.paiements_list, name='paiements_list'),
    path('clients/add-full/', views.client_full_create, name='client_full_create'),
    path('clients/<int:id>/', views.client_detail, name='client_detail'),
    path('clients/<int:id>/edit/', views.client_update, name='client_update'),
    path('clients/<int:id>/delete/', views.client_delete, name='client_delete'),
]