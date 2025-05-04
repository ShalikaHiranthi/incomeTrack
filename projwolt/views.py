from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from earnings.models import Earning  # adjust as needed

def home(request):
    total_earnings = Earning.objects.aggregate(total=Sum('amount'))['total'] or 0

    monthly_earnings = (
        Earning.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    return render(request, 'home.html', {
        'total_earnings': total_earnings,
        'monthly_earnings': monthly_earnings,
    })
