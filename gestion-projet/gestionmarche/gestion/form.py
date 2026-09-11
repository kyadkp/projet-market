from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Client, Cantine, Paiement


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput
    )


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'telephone']


class CantineForm(forms.ModelForm):
    class Meta:
        model = Cantine
        fields = [
            'numero_cantine',
            'superficie',
            'montant_a_payer',
            'bloc',
            'notes',
        ]

        labels = {
            'numero_cantine': 'Numéro de cantine',
            'superficie': 'Superficie',
            'montant_a_payer': 'Montant à payer',
            'bloc': 'Bloc',
            'notes': 'Notes',
        }

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['montant_paye']

        labels = {
            'montant_paye': 'Montant du premier versement',
        }

        widgets = {
            'montant_paye': forms.NumberInput(
                attrs={
                    'min': 0,
                    'placeholder': 'Laisser vide si aucun versement',
                }
            )
        }

    montant_paye = forms.IntegerField(
        required=False,
        min_value=0
    )