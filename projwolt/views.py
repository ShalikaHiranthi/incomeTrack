from django.shortcuts import render
from django.db.models import Sum
from earnings.models import Earning
from gigwork.models import GigWork, WeeklyEarning

def home(request):
    total_earnings = 0
    total_gigs = 0
    user = request.user
    if request.user.is_authenticated:

        total_earnings = (
            Earning.objects.filter(user=user)
            .aggregate(total=Sum('sub_total'))['total'] or 0
        )

        total_gigs = (
                GigWork.objects.filter(user=user)
                .aggregate(total=Sum('total_pay'))['total'] or 0
            )
        
        

    return render(request, 'home.html', {
        'total_earnings': total_earnings,
        'total_gigs': total_gigs
    })
