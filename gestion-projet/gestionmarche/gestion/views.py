from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, Q

from .form import LoginForm, ClientForm, CantineForm, PaiementForm
from .models import Client, Cantine, Paiement


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

    # Statistiques globales
    total_clients = clients.count()
    total_cantines = cantines.count()

    # Total réellement versé
    total_paye = (
        paiements.aggregate(total=Sum('montant_paye'))['total']
        or 0
    )

    # Total à payer pour toutes les cantines
    total_a_payer = (
        cantines.aggregate(total=Sum('montant_a_payer'))['total']
        or 0
    )

    # Dette globale
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


@login_required
def clients_list(request):
    query = request.GET.get('q', '').strip()

    clients = Client.objects.prefetch_related(
        'cantine_set__paiement_set'
    )

    if query:
        clients = clients.filter(
            Q(nom__icontains=query)
            | Q(telephone__icontains=query)
            | Q(cantine__numero_cantine__icontains=query)
            | Q(cantine__superficie__icontains=query)
        ).distinct()

    return render(
        request,
        'gestion/client/list.html',
        {
            'clients': clients,
            'query': query
        }
    )


@login_required
def client_full_create(request):
    """
    Création d'un nouveau client avec sa première cantine.
    Le premier versement est facultatif.
    """

    if request.method == 'POST':

        client_form = ClientForm(request.POST)
        cantine_form = CantineForm(request.POST)
        paiement_form = PaiementForm(request.POST)

        if (
            client_form.is_valid()
            and cantine_form.is_valid()
            and paiement_form.is_valid()
        ):

            with transaction.atomic():

                # Création ou récupération du client
                nom = client_form.cleaned_data['nom']
                telephone = client_form.cleaned_data['telephone']

                client, created = Client.objects.get_or_create(
                    nom=nom,
                    telephone=telephone
                )

                # Création de la cantine
                cantine = cantine_form.save(commit=False)
                cantine.client = client
                cantine.save()

                # Premier versement facultatif
                montant_paye = paiement_form.cleaned_data.get(
                    'montant_paye'
                )

                if montant_paye is not None:

                    from django.utils import timezone

                    paiement = paiement_form.save(commit=False)
                    paiement.cantine = cantine

                    # Date et heure automatiques pour un nouveau versement
                    paiement.date_paiement = timezone.now()
                    paiement.heure_inconnue = False

                    paiement.save()

            return redirect(
                'client_detail',
                id=client.id
            )

    else:
        client_form = ClientForm()
        cantine_form = CantineForm()
        paiement_form = PaiementForm()

    return render(
        request,
        'gestion/client/fullform.html',
        {
            'client_form': client_form,
            'cantine_form': cantine_form,
            'paiement_form': paiement_form,
        }
    )


@login_required
def cantines_list(request):
    query = request.GET.get('q', '').strip()

    cantines = Cantine.objects.select_related('client')

    if query:
        cantines = cantines.filter(
            Q(numero_cantine__icontains=query)
            | Q(superficie__icontains=query)
            | Q(client__nom__icontains=query)
        )

    return render(
        request,
        'gestion/cantines/list.html',
        {
            'cantines': cantines,
            'query': query
        }
    )


@login_required
def paiements_list(request):
    query = request.GET.get('q', '').strip()

    paiements = Paiement.objects.select_related(
        'cantine',
        'cantine__client'
    ).order_by('-date_paiement')

    if query:
        paiements = paiements.filter(
            Q(cantine__client__nom__icontains=query)
            | Q(cantine__numero_cantine__icontains=query)
            | Q(montant_paye__icontains=query)
        )

    return render(
        request,
        'gestion/paiements/list.html',
        {
            'paiements': paiements,
            'query': query
        }
    )


@login_required
def client_detail(request, id):
    client = get_object_or_404(Client, id=id)

    cantines = (
        Cantine.objects
        .filter(client=client)
        .prefetch_related('paiement_set')
    )

    for cantine in cantines:

        paiements = cantine.paiement_set.all()

        total_paye = sum(
            paiement.montant_paye
            for paiement in paiements
        )

        cantine.total_paye = total_paye
        cantine.total_du = cantine.montant_a_payer
        cantine.restant = (
            cantine.montant_a_payer - total_paye
        )

    return render(
        request,
        'gestion/client/details.html',
        {
            'client': client,
            'cantines': cantines
        }
    )


@login_required
def client_update(request, id):
    """
    Modification des informations générales du client.
    Les cantines et les versements sont maintenant
    modifiés séparément.
    """

    client = get_object_or_404(Client, id=id)

    if request.method == 'POST':

        client_form = ClientForm(
            request.POST,
            instance=client
        )

        if client_form.is_valid():
            client_form.save()
            return redirect(
                'client_detail',
                id=client.id
            )

    else:
        client_form = ClientForm(instance=client)

    return render(
        request,
        'gestion/client/update.html',
        {
            'client': client,
            'client_form': client_form,
        }
    )


@login_required
def cantine_create_for_client(request, id):
    """
    Ajoute une nouvelle cantine à un client existant.
    Le premier versement est facultatif.
    """

    client = get_object_or_404(Client, id=id)

    if request.method == 'POST':

        cantine_form = CantineForm(request.POST)
        paiement_form = PaiementForm(request.POST)

        if cantine_form.is_valid() and paiement_form.is_valid():

            with transaction.atomic():

                # Création de la nouvelle cantine
                cantine = cantine_form.save(commit=False)
                cantine.client = client
                cantine.save()

                # Premier versement facultatif
                montant_paye = paiement_form.cleaned_data.get(
                    'montant_paye'
                )

                if montant_paye is not None:

                    from django.utils import timezone

                    paiement = paiement_form.save(commit=False)
                    paiement.cantine = cantine

                    # Date et heure automatiques
                    paiement.date_paiement = timezone.now()
                    paiement.heure_inconnue = False

                    paiement.save()

            return redirect(
                'client_detail',
                id=client.id
            )

    else:
        cantine_form = CantineForm()
        paiement_form = PaiementForm()

    return render(
        request,
        'gestion/client/cantine_create.html',
        {
            'client': client,
            'cantine_form': cantine_form,
            'paiement_form': paiement_form,
        }
       )

@login_required
def cantine_update(request, id):
    """
    Modification d'une cantine précise.
    """

    cantine = get_object_or_404(Cantine, id=id)

    if request.method == 'POST':

        form = CantineForm(
            request.POST,
            instance=cantine
        )

        if form.is_valid():
            form.save()

            return redirect(
                'client_detail',
                id=cantine.client.id
            )

    else:
        form = CantineForm(instance=cantine)

    return render(
        request,
        'gestion/client/cantine_update.html',
        {
            'form': form,
            'cantine': cantine,
        }
    )

@login_required
def paiement_add(request, id):
    """
    Ajout d'un nouveau versement pour une cantine.

    La date et l'heure sont enregistrées automatiquement
    au moment du versement.
    """

    cantine = get_object_or_404(Cantine, id=id)

    if request.method == 'POST':

        form = PaiementForm(request.POST)

        if form.is_valid():

            from django.utils import timezone

            paiement = form.save(commit=False)

            paiement.cantine = cantine
            paiement.date_paiement = timezone.now()
            paiement.heure_inconnue = False

            paiement.save()

            return redirect(
                'client_detail',
                id=cantine.client.id
            )

    else:
        form = PaiementForm()

    return render(
        request,
        'gestion/client/paiement_add.html',
        {
            'form': form,
            'cantine': cantine,
        }
    )


@login_required
def paiement_update(request, id):
    """
    Modification d'un versement existant.
    """

    paiement = get_object_or_404(Paiement, id=id)

    if request.method == 'POST':

        form = PaiementForm(
            request.POST,
            instance=paiement
        )

        if form.is_valid():
            form.save()

            return redirect(
                'client_detail',
                id=paiement.cantine.client.id
            )

    else:
        form = PaiementForm(instance=paiement)

    return render(
        request,
        'gestion/client/paiement_update.html',
        {
            'form': form,
            'paiement': paiement,
        }
    )


@login_required
def paiement_delete(request, id):
    """
    Suppression d'un versement existant.
    """

    paiement = get_object_or_404(Paiement, id=id)

    client_id = paiement.cantine.client.id

    if request.method == 'POST':
        paiement.delete()

        return redirect(
            'client_detail',
            id=client_id
        )

    return render(
        request,
        'gestion/client/paiement_delete.html',
        {
            'paiement': paiement,
        }
    )


@login_required
def client_delete(request, id):
    client = get_object_or_404(Client, id=id)

    if request.method == 'POST':
        client.delete()
        return redirect('clients_list')

    return render(
        request,
        'gestion/client/confirm_delete.html',
        {
            'client': client
        }
    )