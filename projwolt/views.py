from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from earnings.models import Earning  # adjust as needed

def home(request):
    user = request.user
    if request.user.is_authenticated:

        total_earnings = (
            Earning.objects.filter(user=user)
            .aggregate(total=Sum('amount'))['total'] or 0
        )

        monthly_earnings = (
            Earning.objects.filter(user=user)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
    else:
        total_earnings = 0
        monthly_earnings = []

    return render(request, 'home.html', {
        'total_earnings': total_earnings,
        'monthly_earnings': monthly_earnings,
    })
