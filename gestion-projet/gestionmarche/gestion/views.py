from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from .form import LoginForm, ClientForm, CantineForm, PaiementForm
from django.contrib.auth.decorators import login_required
from .models import Client, Cantine, Paiement
from django.db.models import Sum, Q
from django.db import transaction
from django.db.models import Prefetch

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('clients_list')
    else:
        form = LoginForm()

    return render(request, 'gestion/login.html', {'form': form})


@login_required
def dashboard(request):

    clients = Client.objects.all()
    cantines = Cantine.objects.all()
    paiements = Paiement.objects.all()

    # 📊 STATS GLOBALES
    total_clients = clients.count()
    total_cantines = cantines.count()

    total_paye = paiements.aggregate(total=Sum('montant_paye'))['total'] or 0
    total_a_payer = paiements.aggregate(total=Sum('montant_a_payer'))['total'] or 0

    # 💰 DETTE GLOBALE
    total_restant = total_a_payer - total_paye

    context = {
        'clients': clients,
        'cantines': cantines,
        'paiements': paiements,

        'total_clients': total_clients,
        'total_cantines': total_cantines,

        'total_paye': total_paye,
        'total_a_payer': total_a_payer,
        'total_restant': total_restant,
    }

    return render(request, 'gestion/dashboard.html', context)


def clients_list(request):
    query = request.GET.get('q', '')

    clients = Client.objects.prefetch_related('cantine_set__paiement_set')

    if query:
        clients = clients.filter(
            Q(nom__icontains=query) |
            Q(telephone__icontains=query) |
            Q(cantine__matricule__icontains=query) |
            Q(cantine__superficie__icontains=query)
        ).distinct()

    return render(request, 'gestion/client/list.html', {
        'clients': clients,
        'query': query
    })



@login_required
def client_full_create(request):

    if request.method == 'POST':

        client_form = ClientForm(request.POST)
        cantine_form = CantineForm(request.POST)
        paiement_form = PaiementForm(request.POST)

        if client_form.is_valid() and cantine_form.is_valid() and paiement_form.is_valid():

            with transaction.atomic():

                # 🔥 récupérer données client
                nom = client_form.cleaned_data['nom']
                telephone = client_form.cleaned_data['telephone']

                # 🔥 client unique
                client, created = Client.objects.get_or_create(
                    nom=nom,
                    telephone=telephone
                )

                # 🔥 cantine
                cantine = cantine_form.save(commit=False)
                cantine.client = client
                cantine.save()

                # 🔥 paiement
                paiement = paiement_form.save(commit=False)
                paiement.cantine = cantine
                paiement.save()

            return redirect('clients_list')

    else:
        client_form = ClientForm()
        cantine_form = CantineForm()
        paiement_form = PaiementForm()

    return render(request, 'gestion/client/fullform.html', {
        'client_form': client_form,
        'cantine_form': cantine_form,
        'paiement_form': paiement_form,
    })

def cantines_list(request):
    query = request.GET.get('q')

    cantines = Cantine.objects.all()

    if query:
        cantines = cantines.filter(
            Q(matricule__icontains=query) |
            Q(localisation__icontains=query) |
            Q(client__nom__icontains=query)
        )

    return render(request, 'gestion/cantines/list.html', {
        'cantines': cantines,
        'query': query
    })


def paiements_list(request):
    query = request.GET.get('q')

    paiements = Paiement.objects.all()

    if query:
        paiements = paiements.filter(
            Q(cantine__client__nom__icontains=query) |
            Q(montant_paye__icontains=query)
        )

    return render(request, 'gestion/paiements/list.html', {
        'paiements': paiements,
        'query': query
    })


def client_detail(request, id):
    client = get_object_or_404(Client, id=id)

    cantines = Cantine.objects.filter(client=client).prefetch_related('paiement_set')

    for cantine in cantines:
        paiements = cantine.paiement_set.all()

        total_paye = sum(p.montant_paye for p in paiements)

        cantine.total_paye = total_paye
        cantine.total_du = cantine.montant_a_payer
        cantine.restant = cantine.montant_a_payer - total_paye

    return render(request, 'gestion/client/details.html', {
        'client': client,
        'cantines': cantines
    })




def client_update(request, id):
    client = get_object_or_404(Client, id=id)

    # ⚠️ on récupère UNE cantine et UN paiement (version simple)
    cantine = client.cantine_set.first()
    paiement = None

    if cantine:
        paiement = cantine.paiement_set.first()

    if request.method == 'POST':
        client_form = ClientForm(request.POST, instance=client)
        cantine_form = CantineForm(request.POST, instance=cantine)
        paiement_form = PaiementForm(request.POST, instance=paiement)

        if client_form.is_valid() and cantine_form.is_valid() and paiement_form.is_valid():
            client = client_form.save()

            cantine = cantine_form.save(commit=False)
            cantine.client = client
            cantine.save()

            paiement = paiement_form.save(commit=False)
            paiement.cantine = cantine
            paiement.save()

            return redirect('clients_list')

    else:
        # 🔥 PRÉ-REMPLISSAGE AUTOMATIQUE
        client_form = ClientForm(instance=client)
        cantine_form = CantineForm(instance=cantine)
        paiement_form = PaiementForm(instance=paiement)

    return render(request, 'gestion/client/update.html', {
        'client_form': client_form,
        'cantine_form': cantine_form,
        'paiement_form': paiement_form,
    })

def client_delete(request, id):
    client = get_object_or_404(Client, id=id)

    if request.method == 'POST':
        client.delete()
        return redirect('clients_list')

    return render(request, 'gestion/client/confirm_delete.html', {'client': client})