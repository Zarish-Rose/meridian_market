from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Store

@login_required
def store_list(request):
    stores = Store.objects.filter(owner=request.user)
    return render(request, 'stores/store_list.html', {'stores': stores})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import StoreForm

@login_required
def create_store(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            return redirect('store_list')
    else:
        form = StoreForm()

    return render(request, 'stores/create_store.html', {'form': form})

from django.shortcuts import get_object_or_404

@login_required
def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    return render(request, 'stores/store_detail.html', {'store': store})

    # Owners can only access their own stores
