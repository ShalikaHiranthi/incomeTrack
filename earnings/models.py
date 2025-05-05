from django.db import models
from django.contrib.auth.models import User

class Earning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.source} - {self.amount}"
