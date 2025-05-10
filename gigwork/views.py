from django.shortcuts import render, redirect, get_object_or_404
from .forms import GigWorkForm
from .models import GigWork
from django.contrib.auth.decorators import login_required
import datetime
from .forms import ExcelImportForm
import pandas as pd
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear
from django.db.models import Sum, F, Func, IntegerField, Value, Case, When
from django.http import HttpResponse
from django.db.models.functions import TruncMonth
from collections import defaultdict
import logging
logger = logging.getLogger(__name__)


@login_required
def add_gigwork(request):
    if request.method == 'POST':
        form = GigWorkForm(request.POST)
        if form.is_valid():
            gig = form.save(commit=False)
            gig.user = request.user
            gig.save()
            return redirect('gigwork_list')
    else:
        form = GigWorkForm()
    return render(request, 'gigwork/form.html', {'form': form})

@login_required
def gigwork_list(request):
    gigs = GigWork.objects.filter(user=request.user)
    
    total = 0
    for gig in gigs:
        total += gig.total_pay

    return render(request, 'gigwork/list.html', {
        'gigs': gigs,
        'total_earnings': total
    })

@login_required
def gigwork_edit(request, id):
    gigwork = get_object_or_404(GigWork, id=id, user=request.user)

    if request.method == 'POST':
        form = GigWorkForm(request.POST, instance=gigwork)
        if form.is_valid():
            form.save()
            return redirect('gigwork_list')
    else:
        form = GigWorkForm(instance=gigwork)

    return render(request, 'gigwork/form.html', {'form': form, 'gigwork': gigwork})


@login_required
def gigwork_delete(request, id):
    gigwork = get_object_or_404(GigWork, id=id)
    gigwork.delete()
    return redirect('gigwork_list')


@login_required
def import_gigwork(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file)
            df['date'] = pd.to_datetime(df['date']).dt.date  # Ensure proper date format

            user = request.user  # Logged-in user

            for _, row in df.iterrows():
                if pd.isna(row['duration']) or pd.isna(row['distance_km']) or pd.isna(row['date']):
                    continue  # Skip this row
                # hours = int(row['duration'])
                # minutes = int(round((row['duration'] - hours) * 100))
                # duration = timedelta(hours=hours, minutes=minutes)
                total_minutes = float(row['duration'])

                gig = GigWork(
                    user=user,
                    delivery_details='Imported from Excel',
                    duration=total_minutes,
                    distance_km=row['distance_km'],
                    date=row['date']
                )
                gig.save()
            return redirect('gigwork_list')
    else:
        form = ExcelImportForm()
    return render(request, 'gigwork/import_gigwork.html', {'form': form})

def get_half_month_totals(user=None):
    from .models import GigWork  # adjust if you're placing this in a different file

    qs = GigWork.objects.all()

    if user:
        qs = qs.filter(user=user)

    qs = qs.annotate(
        year=ExtractYear('date'),
        month=ExtractMonth('date'),
        day=ExtractDay('date'),
        half=Case(
            When(day__lte=15, then=Value(1)),
            default=Value(2),
            output_field=IntegerField()
        )
    ).values('user', 'year', 'month', 'half').annotate(
        total_earning=Sum('earning'),
        total_fuel=Sum('fuel_pay'),
        total_total=Sum('total_pay')
    ).order_by('user', 'year', 'month', 'half')

    return qs

@login_required
def export_gigs_excel(request):
    gigs = GigWork.objects.filter().values('date', 'duration', 'duration_min', 'distance_km', 'earning', 'fuel_pay', 'total_pay')

    if not gigs:
        return HttpResponse("No earnings to export.", content_type="text/plain")

    df = pd.DataFrame(gigs)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=gigs.xlsx'
    df.to_excel(response, index=False, engine='openpyxl')

    return response

@login_required
def sort_gigs(request):
    
    user = request.user

    if request.user.is_authenticated:

        total_earnings = (
            GigWork.objects.filter(user=user)
            .aggregate(total=Sum('total_pay'))['total'] or 0
        )

        monthly_earnings = (
            GigWork.objects.filter(user=user)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('total_pay'))
            .order_by('month')
        )

        earnings_by_half_month = defaultdict(lambda: {"start": 0, "end": 0})

        if user.is_authenticated:
            earnings = GigWork.objects.filter(user=user)

            for earning in earnings:
                month_key = earning.date.strftime("%Y-%m")

                if earning.date.day <= 15:
                    earnings_by_half_month[month_key]["start"] += earning.total_pay
                else:
                    earnings_by_half_month[month_key]["end"] += earning.total_pay

        # Convert to list of dicts sorted by month
        sorted_earnings = sorted(
            [{
                "month": k,
                "start": v["start"],
                "end": v["end"],
                "total": v["start"] + v["end"]
            } for k, v in earnings_by_half_month.items()],
            key=lambda x: x["month"]
        )
        logging.debug(sorted_earnings)
            
        
    else:
        total_earnings = 0
        monthly_earnings = []
        sorted_earnings = []

    return render(request, 'gigwork/list_sort.html', {
        'earnings': earnings,
        'total_earnings': total_earnings,
        'monthly_earnings': monthly_earnings,
        'half_month_earnings': sorted_earnings
    })
