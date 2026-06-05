from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Event

# Create your views here.
def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    context = {
        'events_count': Event.objects.count(),
    }
    return render(request, 'dashboard.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)   # log the new user in automatically
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
