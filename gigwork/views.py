from django.shortcuts import render, redirect, get_object_or_404
from .forms import GigWorkForm
from .models import GigWork
from django.contrib.auth.decorators import login_required
import datetime
from .forms import ExcelImportForm
import pandas as pd
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear
from django.db.models import Sum, F, Func, IntegerField, Value, Case, When


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
    return render(request, 'gigwork/list.html', {'gigs': gigs})

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
