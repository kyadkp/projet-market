from django.db import models

# Client (locataire)
class Client(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nom


# Cantine (ou stand)
class Cantine(models.Model):
    matricule = models.CharField(max_length=50, unique=True)
    localisation = models.CharField(max_length=100)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return self.matricule


# Paiement (loyer)
class Paiement(models.Model):
    cantine = models.ForeignKey(Cantine, on_delete=models.CASCADE)
    montant_a_payer = models.DecimalField(max_digits=10, decimal_places=2)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateField()

    def __str__(self):
        return f"{self.cantine} - {self.date_paiement}"