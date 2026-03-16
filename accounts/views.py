from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import ProfileForm
from .models import Profile
from stores.models import Store


def index(request):
    return render(request, 'home/home.html')


def about(request):
    return render(request, 'home/about.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts_index')
    else:
        form = UserCreationForm()

    return render(request, 'home/register.html', {'form': form})


@login_required
def my_profile(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('my_profile')
    else:
        form = ProfileForm(instance=profile)

    if profile.role == 'owner':
        store = Store.objects.filter(owner=user).first()
    elif profile.role in ['staff', 'manager']:
        store = Store.objects.filter(members__user=user).distinct().first()
    elif profile.role == 'admin':
        store = Store.objects.first()
    else:
        store = None

    context = {'store': store, 'form': form}
    return render(request, 'accounts/my_profile.html', context)
