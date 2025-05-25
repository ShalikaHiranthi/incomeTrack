from django.db import models
from django.contrib.auth.models import User

class Earning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=100)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_tip = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField()

    def __str__(self):
        return f"{self.title} - {self.sub_total}"
    
class EarningDetail(models.Model):
    earning = models.ForeignKey(Earning, on_delete=models.CASCADE, related_name='details')
    source = models.CharField(max_length=100)
    date = models.DateField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tip = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self.earning and not self.date:
            self.date = self.earning.date
        super().save(*args, **kwargs)

    def subtotal(self):
        return self.amount + self.tip

    def __str__(self):
        return f"{self.source} - {self.total}"
    
class Weeklypayments(models.Model):
    YES_NO_CHOICES = [
        ("Yes", "Yes"),
        ("Next", "Next"),
        ("No", "No"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    start = models.DecimalField(max_digits=10, decimal_places=2)
    total_tips1 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount1 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    per30_1 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    netpay1 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ispaid_part1 = models.CharField(max_length=4, choices=YES_NO_CHOICES)
    end = models.DecimalField(max_digits=10, decimal_places=2)
    total_tips2 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount2 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    per30_2 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    netpay2 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ispaid_part2 = models.CharField(max_length=4, choices=YES_NO_CHOICES)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    nettotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%Y-%m')}"