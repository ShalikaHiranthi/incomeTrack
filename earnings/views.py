from django.shortcuts import render, redirect, get_object_or_404
from .models import Earning
from .forms import EarningForm

def earning_list(request):
    earnings = Earning.objects.all()
    return render(request, 'earnings/list.html', {'earnings': earnings})

def add_earning(request):
    if request.method == 'POST':
        form = EarningForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('earning_list')
    else:
        form = EarningForm()
    return render(request, 'earnings/form.html', {'form': form})

def delete_earning(request, pk):
    earning = get_object_or_404(Earning, pk=pk)
    earning.delete()
    return redirect('earning_list')
