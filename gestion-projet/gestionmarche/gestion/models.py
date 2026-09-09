from django.db import models

class Client(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        unique_together = ['nom', 'telephone']

    def __str__(self):
        return self.nom


class Cantine(models.Model):
    BLOCS = [('A', 'Bloc A'), ('B', 'Bloc B'), ('C', 'Bloc C'), ('D', 'Bloc D')]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    matricule = models.CharField(max_length=100, unique=True)
    superficie = models.CharField(max_length=50)   # ex: "32 m² + 4 m²"
    montant_a_payer = models.BigIntegerField(default=0)
    bloc = models.CharField(max_length=1, choices=BLOCS, default='B')
    notes = models.TextField(blank=True, default='')   # pour les "AV", "Diakhmpa", etc.
    est_vacant = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.matricule} - {self.client}"


class Paiement(models.Model):
    cantine = models.ForeignKey(Cantine, on_delete=models.CASCADE)
    montant_paye = models.IntegerField()
    date_paiement = models.DateField()

    def __str__(self):
        return f"{self.cantine} - {self.montant_paye}"