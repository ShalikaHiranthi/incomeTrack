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
    
class WeeklyEarning(models.Model):
    YES_NO_CHOICES = [
        ("Yes", "Yes"),
        ("Next", "Next"),
        ("No", "No"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    start = models.DecimalField(max_digits=10, decimal_places=2)
    netpay1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ispaid_part1 = models.CharField(max_length=4, choices=YES_NO_CHOICES)
    end = models.DecimalField(max_digits=10, decimal_places=2)
    netpay2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ispaid_part2 = models.CharField(max_length=4, choices=YES_NO_CHOICES)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    nettotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%Y-%m')}"
