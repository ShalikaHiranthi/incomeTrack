from django.db import models
from django.contrib.auth.models import User

class GigWork(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_details = models.TextField()
    duration_min = models.FloatField(default=0.0)
    duration = models.FloatField(default=0.0)
    distance_km = models.FloatField(default=0.0)
    earning = models.FloatField(blank=True, null=True)
    fuel_pay = models.FloatField(blank=True, null=True)
    total_pay = models.FloatField(blank=True, null=True)
    date = models.DateField()

    def save(self, *args, **kwargs):
        hours = int(self.duration)
        minutes = int(round((self.duration - hours) * 100))
        self.duration_min = hours * 60 + minutes

        self.earning = self.duration_min * (11 / 60)
        self.fuel_pay = self.distance_km * 0.59
        self.total_pay = self.earning + self.fuel_pay
        super().save(*args, **kwargs)

    def __str__(self):
        return f"GigWork on {self.date} for {self.user.username}"
