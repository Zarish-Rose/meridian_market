from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Store

@login_required
def store_list(request):
    stores = Store.objects.filter(owner=request.user)
    return render(request, 'stores/store_list.html', {'stores': stores})
