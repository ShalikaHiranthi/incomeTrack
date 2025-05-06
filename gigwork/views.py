from django.shortcuts import render, redirect, get_object_or_404
from .forms import GigWorkForm
from .models import GigWork
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from .forms import ExcelImportForm
import pandas as pd


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

            user = request.user  # Logged-in user

            for _, row in df.iterrows():
                hours = int(row['duration'])
                minutes = int(round((row['duration'] - hours) * 100))
                duration = timedelta(hours=hours, minutes=minutes)

                gig = GigWork(
                    user=user,
                    delivery_details='Imported from Excel',
                    duration=duration,
                    distance_km=row['distance_km'],
                    date=row['date']
                )
                gig.save()
            return redirect('gigwork_list')
    else:
        form = ExcelImportForm()
    return render(request, 'gigwork/import_gigwork.html', {'form': form})
