from django.shortcuts import render, redirect, get_object_or_404
from .forms import GigWorkForm, WeeklyEarningForm
from .models import GigWork, WeeklyEarning
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .forms import ExcelImportForm
import pandas as pd
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear
from django.db.models import Sum, F, Func, IntegerField, Value, Case, When
from django.http import HttpResponse
from django.db.models.functions import TruncMonth
from collections import defaultdict
from django.utils.timezone import now
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
    monthgigs = WeeklyEarning.objects.filter(user=request.user)

    month = request.GET.get('month')  # format: YYYY-MM
    if month:
        try:
            date_obj = datetime.strptime(month, '%Y-%m')
            gigs = gigs.filter(date__year=date_obj.year, date__month=date_obj.month)
        except ValueError:
            pass  # optionally handle invalid input

    total = sum(gig.total_pay or 0 for gig in gigs)
    nettotal = sum(monthgig.nettotal or 0 for monthgig in monthgigs)

    return render(request, 'gigwork/list.html', {
        'gigs': gigs,
        'total_gigs': total,
        'nettotal_gigs': nettotal,
        'selected_month': month,
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
    earnings = []
    total_gigs = 0
    sorted_earnings = []
    monthly_data = []

    if request.user.is_authenticated:

        if request.method == 'POST' and request.POST.get("generate") == "1":
            # Current month
            current_date = now()
            current_month_key = current_date.strftime("%Y-%m")

            # Delete only current month entries
            WeeklyEarning.objects.filter(
            user=user,
            month__year=current_date.year,
            month__month=current_date.month
            ).delete()

            # Filter gigs for the current month only
            earnings = GigWork.objects.filter(
                user=user,
                date__year=current_date.year,
                date__month=current_date.month
            )

            # Process gig data
            # earnings = GigWork.objects.filter(user=user)
            earnings_by_half_month = defaultdict(lambda: {"start": 0, "end": 0})

            for earning in earnings:
                if earning.date.day <= 15:
                    earnings_by_half_month[current_month_key]["start"] += earning.total_pay
                else:
                    earnings_by_half_month[current_month_key]["end"] += earning.total_pay
            net1 = 0
            net2 = 0
            totalnet=0
            for k, v in earnings_by_half_month.items():
                
                total = v["start"] + v["end"]
                month_date = datetime.strptime(k + "-01", "%Y-%m-%d")
                net1 = v["start"] - (v["start"]*3.99/100)- (v["start"]*2/100)
                net2 = v["end"] - (v["end"]*3.99/100) - (v["end"]*2/100)
                totalnet = net1 + net2
                
                # Save to database
                WeeklyEarning.objects.create(
                    user=user,
                    month=month_date,
                    start=v["start"],
                    netpay1 = net1,
                    end=v["end"],
                    netpay2 = net2,
                    total=total,
                    nettotal=totalnet
                )

            # Fetch for display
            sorted_earnings = WeeklyEarning.objects.filter(user=user).order_by('month')
            

        else:
            sorted_earnings = WeeklyEarning.objects.filter(user=user).order_by('month')
            total_gigs = (
                GigWork.objects.filter(user=user)
                .aggregate(total=Sum('total_pay'))['total'] or 0
            )

        # Get monthly data with month and total earnings
        raw_monthly_data = WeeklyEarning.objects.filter(user=user).annotate(month_annotated=TruncMonth('month')).values('month_annotated').annotate(
            start=Sum('start'), 
            end=Sum('end'),
            total=Sum('total')
        ).order_by('month_annotated')

        # Convert to a JSON-safe structure (datetime and Decimal to float)
        monthly_data = [
            {
                'month': entry['month_annotated'].strftime('%Y-%m'),  # Format the date as YYYY-MM
                'start': float(entry['start']),
                'end': float(entry['end']),
                'total': float(entry['total'])  # Convert the Decimal to float
            }
            for entry in raw_monthly_data
        ]

    return render(request, 'gigwork/list_sort.html', {
        'total_gigs': total_gigs,
        'monthly_data': monthly_data,
        'half_month_earnings': sorted_earnings
    })

@login_required
def update_weekly_earning(request, id):
    week = get_object_or_404(WeeklyEarning, id=id, user=request.user)

    if request.method == 'POST':
        form = WeeklyEarningForm(request.POST, instance=week)
        #logging.debug(request.POST.get("ispaid_part1"))
        if form.is_valid():
            form.save()
            return redirect('sort_gigs')
    else:
        form = WeeklyEarningForm(instance=week)

    return render(request, 'gigwork/form.html', {'form': form, 'week': week, 'earning_id':id})