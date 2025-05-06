from django.shortcuts import render, redirect, get_object_or_404
from .models import Earning
from .forms import EarningForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.http import HttpResponse
from django.db.models import F, Sum, ExpressionWrapper, DecimalField

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # name of login route from auth.urls
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def earning_list(request):
    earnings = Earning.objects.filter(user=request.user)

    total_earnings = earnings.aggregate(
        total=Sum(ExpressionWrapper(F('amount') + F('tip'), output_field=DecimalField()))
    )['total'] or 0

    return render(request, 'earnings/list.html', {
        'earnings': earnings,
        'total_earnings': total_earnings
    })

@login_required
def add_earning(request):
    if request.method == 'POST':
        form = EarningForm(request.POST)
        if form.is_valid():
            earning = form.save(commit=False)
            earning.user = request.user
            earning.total = earning.amount + earning.tip
            earning.save()
            return redirect('earning_list')
    else:
        form = EarningForm()
    return render(request, 'earnings/form.html', {'form': form})

@login_required
def edit_earning(request, pk):
    earning = get_object_or_404(Earning, pk=pk, user=request.user)

    if request.method == 'POST':
        form = EarningForm(request.POST, instance=earning)
        if form.is_valid():
            updated_earning = form.save(commit=False)
            updated_earning.total = updated_earning.amount + updated_earning.tip
            updated_earning.save()
            return redirect('earning_list')
    else:
        form = EarningForm(instance=earning)

    return render(request, 'earnings/form.html', {'form': form})

@login_required
def export_earnings_excel(request):
    earnings = Earning.objects.filter(user=request.user).values('date', 'source', 'amount', 'tip', 'total')

    if not earnings:
        return HttpResponse("No earnings to export.", content_type="text/plain")

    df = pd.DataFrame(earnings)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=earnings.xlsx'
    df.to_excel(response, index=False, engine='openpyxl')

    return response

@login_required
def delete_earning(request, pk):
    earning = get_object_or_404(Earning, pk=pk)
    earning.delete()
    return redirect('earning_list')

