from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Client, Cantine, Paiement
from datetime import date

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput)
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'telephone']


class CantineForm(forms.ModelForm):
    class Meta:
        model = Cantine
        fields = ['matricule', 'superficie' , 'montant_a_payer']


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['montant_paye', 'date_paiement']
        widgets = {
            'date_paiement': forms.DateInput(
                attrs={
                    'type': 'date',
                    'max': date.today().isoformat() 
                }
            )
        }
