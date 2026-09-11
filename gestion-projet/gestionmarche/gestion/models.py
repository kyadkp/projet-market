from django.db import models


class Client(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        unique_together = ['nom', 'telephone']

    def __str__(self):
        return self.nom


class Cantine(models.Model):
    BLOCS = [
        ('A', 'Bloc A'),
        ('B', 'Bloc B'),
        ('C', 'Bloc C'),
        ('D', 'Bloc D'),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    numero_cantine = models.CharField(max_length=100)
    superficie = models.CharField(max_length=50)
    montant_a_payer = models.BigIntegerField(default=0)
    bloc = models.CharField(max_length=1, choices=BLOCS, default='B')
    notes = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.numero_cantine} - {self.client}"

class Paiement(models.Model):
    cantine = models.ForeignKey(
        Cantine,
        on_delete=models.CASCADE
    )

    montant_paye = models.IntegerField()

    date_paiement = models.DateTimeField(
        null=True,
        blank=True
    )

    heure_inconnue = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.cantine} - {self.montant_paye}"