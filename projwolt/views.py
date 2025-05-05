from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from earnings.models import Earning
from collections import defaultdict

def home(request):
    user = request.user
    if request.user.is_authenticated:

        total_earnings = (
            Earning.objects.filter(user=user)
            .aggregate(total=Sum('total'))['total'] or 0
        )

        monthly_earnings = (
            Earning.objects.filter(user=user)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('total'))
            .order_by('month')
        )

        earnings_by_half_month = defaultdict(lambda: {"start": 0, "end": 0})

        if user.is_authenticated:
            earnings = Earning.objects.filter(user=user)

            for earning in earnings:
                month_key = earning.date.strftime("%Y-%m")
                if earning.date.day <= 15:
                    earnings_by_half_month[month_key]["start"] += earning.total
                else:
                    earnings_by_half_month[month_key]["end"] += earning.total

        # Convert to list of dicts sorted by month
        sorted_earnings = sorted(
            [{"month": k, **v} for k, v in earnings_by_half_month.items()],
            key=lambda x: x["month"]
        )
    else:
        total_earnings = 0
        monthly_earnings = []
        sorted_earnings = []

    return render(request, 'home.html', {
        'total_earnings': total_earnings,
        'monthly_earnings': monthly_earnings,
        'half_month_earnings': sorted_earnings
    })
