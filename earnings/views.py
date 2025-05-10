from django.shortcuts import render, redirect, get_object_or_404
from .models import Earning, EarningDetail
from .forms import EarningForm, EarningDetailForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.http import HttpResponse
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth
from collections import defaultdict

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

    total_earnings = 0
    for earning in earnings:
        total_earnings += earning.sub_total
    
    return render(request, 'earnings/list.html', {
        'earnings': earnings,
        'total_earnings': total_earnings
    })

@login_required
def earning_list_sort(request):
    total_earnings = 0
    monthly_earnings = []
    sorted_earnings = []
    
    user = request.user

    if request.user.is_authenticated:

        total_earnings = (
            Earning.objects.filter(user=user)
            .aggregate(total=Sum('sub_total'))['total'] or 0
        )

        monthly_earnings = (
            Earning.objects.filter(user=user)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('sub_total'))
            .order_by('month')
        )

        earnings_by_half_month = defaultdict(lambda: {"start": 0, "end": 0})

        if user.is_authenticated:
            earnings = Earning.objects.filter(user=user)

            for earning in earnings:
                month_key = earning.date.strftime("%Y-%m")
                if earning.date.day <= 15:
                    earnings_by_half_month[month_key]["start"] += earning.sub_total
                else:
                    earnings_by_half_month[month_key]["end"] += earning.sub_total

        # Convert to list of dicts sorted by month
        sorted_earnings = sorted(
            [{"month": k, **v} for k, v in earnings_by_half_month.items()],
            key=lambda x: x["month"]
        )
    
    return render(request, 'earnings/list_sort.html', {
        'earnings': earnings,
        'total_earnings': total_earnings,
        'monthly_earnings': monthly_earnings,
        'half_month_earnings': sorted_earnings
    })

@login_required
def add_earning(request):
    if request.method == 'POST':
        form = EarningForm(request.POST)
        if form.is_valid():
            earning = form.save(commit=False)
            earning.user = request.user
            earning.save()
            return redirect('earning_list')
    else:
        form = EarningForm()
    return render(request, 'earnings/form.html', {'form': form})

@login_required
def add_earning_details(request, id):
    earning = get_object_or_404(Earning, pk=id)
    if request.method == 'POST':
        form = EarningDetailForm(request.POST)
        if form.is_valid():
            earning_d = form.save(commit=False)
            earning_d.earning = earning
            earning_d.user = request.user
            earning_d.total = earning_d.amount + earning_d.tip
            earning_d.save()
            update_subtotal(earning.id)
            return redirect('earning_list_details', id=earning.id)
    else:
        form = EarningDetailForm()
    return render(request, 'earnings/form.html', {'form': form})

def update_subtotal(earning_id):
    earning_details = EarningDetail.objects.filter(earning_id=earning_id)

    total = 0
    for detail in earning_details:
        total += detail.amount + detail.tip

    earning = Earning.objects.get(id=earning_id)
    earning.sub_total = total
    earning.save()
        

@login_required
def earning_list_details(request,id):
    earning_details = EarningDetail.objects.filter(earning_id=id)
    total = 0
    for detail in earning_details:
        sum = detail.amount + detail.tip
        total += sum
    
    total_earnings = total
    return render(request, 'earnings/list_details.html', {
        'earning_details': earning_details,
        'earning_id': id,
        'total_earnings': total_earnings
    })

@login_required
def delete_earning_detail(request, pk):
    earning_details = get_object_or_404(EarningDetail, pk=pk)
    earning_details.delete()
    return redirect('earning_list_details', id=earning_details.earning_id)

@login_required
def edit_earning_detail(request, pk):
    earning_d = get_object_or_404(EarningDetail, pk=pk)

    if request.method == 'POST':
        form = EarningDetailForm(request.POST, instance=earning_d)
        if form.is_valid():
            updated_earning = form.save(commit=False)
            updated_earning.save()
            update_subtotal(earning_d.earning_id)
            return redirect('earning_list_details', id=earning_d.earning_id)
    else:
        form = EarningDetailForm(instance=earning_d)

    return render(request, 'earnings/form.html', {'form': form})

@login_required
def edit_earning(request, pk):
    earning = get_object_or_404(Earning, pk=pk, user=request.user)

    if request.method == 'POST':
        form = EarningForm(request.POST, instance=earning)
        if form.is_valid():
            updated_earning = form.save(commit=False)
            updated_earning.save()
            return redirect('earning_list')
    else:
        form = EarningForm(instance=earning)

    return render(request, 'earnings/form.html', {'form': form})

@login_required
def export_earnings_excel(request):
    earnings = EarningDetail.objects.filter().values('date', 'source', 'amount', 'tip', 'total')

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

