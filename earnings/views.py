from django.shortcuts import render, redirect, get_object_or_404
from .models import Earning, EarningDetail, Weeklypayments
from .forms import EarningForm, EarningDetailForm, ExcelImportForm, WeeklyPayForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.http import HttpResponse
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth
from collections import defaultdict
from datetime import datetime
from django.contrib import messages
import logging
logger = logging.getLogger(__name__)

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
    earnings = EarningDetail.objects.all()

    if not earnings:
        return HttpResponse("No earnings to export.", content_type="text/plain")

    # Extract all fields dynamically if needed
    field_names = [field.name for field in EarningDetail._meta.fields]
    earnings_data = earnings.values(*field_names)  # Include all fields dynamically

    df = pd.DataFrame(earnings_data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=earnings.xlsx'
    df.to_excel(response, index=False, engine='openpyxl')

    return response

@login_required
def delete_earning(request, pk):
    earning = get_object_or_404(Earning, pk=pk)
    earning.delete()
    return redirect('earning_list')

@login_required
def sort_earnings(request):
    user = request.user
    earnings = []
    total_gigs = 0
    sorted_earnings = []
    monthly_data = []

    if request.user.is_authenticated:

        if request.method == 'POST' and request.POST.get("generate") == "1":
            # Clear old entries (optional)
            Weeklypayments.objects.filter(user=user).delete()

            # Process gig data
            earnings = EarningDetail.objects.filter()
            earnings_by_half_month = defaultdict(lambda: {"start": 0, "end": 0})

            for earning in earnings:
                month_key = earning.date.strftime("%Y-%m")
                if earning.date.day <= 15:
                    earnings_by_half_month[month_key]["start"] += earning.total
                else:
                    earnings_by_half_month[month_key]["end"] += earning.total

            for k, v in earnings_by_half_month.items():
                
                total = v["start"] + v["end"]
                month_date = datetime.strptime(k + "-01", "%Y-%m-%d")
                
                # Save to database
                Weeklypayments.objects.create(
                    user=user,
                    month=month_date,
                    start=v["start"],
                    end=v["end"],
                    total=total
                )

            # Fetch for display
            sorted_earnings = Weeklypayments.objects.filter(user=user).order_by('month')
            logging.debug(sorted_earnings)
            

        else:
            sorted_earnings = Weeklypayments.objects.filter(user=user).order_by('month')
            logging.debug(sorted_earnings)
            total_gigs = (
                Earning.objects.filter(user=user)
                .aggregate(total=Sum('sub_total'))['total'] or 0
            )

        # Get monthly data with month and total earnings
        raw_monthly_data = Weeklypayments.objects.filter(user=user).annotate(month_annotated=TruncMonth('month')).values('month_annotated').annotate(
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

    return render(request, 'earnings/list_sort.html', {
        'total_gigs': total_gigs,
        'monthly_data': monthly_data,
        'half_month_earnings': sorted_earnings
    })

@login_required
def import_earnings(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                # Read the Excel file into a DataFrame
                df = pd.read_excel(file)

                # Ensure the 'date' column is in proper date format
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date  # Handle invalid date values
                
                user = request.user  # Get the logged-in user

                # Loop through each row in the DataFrame
                for _, row in df.iterrows():
                    # Skip rows with missing or invalid data
                    if pd.isna(row['amount']) or pd.isna(row['tip']) or pd.isna(row['date']):
                        logger.warning(f"Skipping row with missing data: {row}")
                        continue
                    # Select Earning object based on the 'date'
                    if row['date'] == pd.to_datetime('2025-05-05').date():
                        earning = Earning.objects.get(id=1)
                    elif row['date'] == pd.to_datetime('2025-05-06').date():
                        earning = Earning.objects.get(id=2)
                    elif row['date'] == pd.to_datetime('2025-05-07').date():
                        earning = Earning.objects.get(id=3)
                    elif row['date'] == pd.to_datetime('2025-05-08').date():
                        earning = Earning.objects.get(id=4)
                    elif row['date'] == pd.to_datetime('2025-05-09').date():
                        earning = Earning.objects.get(id=5)
                    else:
                        logger.warning(f"No Earning object found for date: {row['date']}")
                        continue  # Skip if no matching Earning object is found

                    # Create a new Earning record
                    try:
                        earning = EarningDetail(
                            earning=earning,
                            source=row['source'],
                            amount=row['amount'],
                            tip=row['tip'],
                            total=row['total'],
                            date=row['date']
                        )
                        earning.save()
                        logger.info(f"Successfully imported earning: {row['source']}")
                    except Exception as e:
                        logger.error(f"Error saving row: {e}")

                # Redirect to the earnings list page with a success message
                messages.success(request, 'Earnings data imported successfully.')
                return redirect('earning_list')
            except Exception as e:
                logger.error(f"Error processing the file: {e}")
                messages.error(request, 'There was an error processing the file.')
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
    else:
        form = ExcelImportForm()

    return render(request, 'earnings/import.html', {'form': form})

@login_required
def update_weekly_pay(request, id):
    week = get_object_or_404(Weeklypayments, id=id, user=request.user)

    if request.method == 'POST':
        form = WeeklyPayForm(request.POST, instance=week)
        #logging.debug(request.POST.get("ispaid_part1"))
        if form.is_valid():
            form.save()
            return redirect('sort_earnings')
    else:
        form = WeeklyPayForm(instance=week)

    return render(request, 'earnings/form.html', {'form': form, 'week': week, 'earning_id':id})
