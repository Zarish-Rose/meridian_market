from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import store_access_required
from .models import Store
from .forms import StoreForm

@login_required
def store_list(request):
    user = request.user

    if user.profile.role == 'owner':
        stores = Store.objects.filter(owner=user)

    elif user.profile.role == 'staff':
        stores = Store.objects.filter(members__user=user)

    elif user.profile.role == 'admin':
        stores = Store.objects.all()

    else:
        stores = Store.objects.none()

    return render(request, 'stores/store_list.html', {'stores': stores})

@login_required
def create_store(request):
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            return redirect('store_list')
    else:
        form = StoreForm()

    return render(request, 'stores/create_store.html', {'form': form})

@login_required
@store_access_required
def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    return render(request, 'stores/store_detail.html', {'store': store})

    # Owners can only access their own stores

@login_required
@store_access_required
def edit_store(request, store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)

    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            return redirect('store_detail', store_id=store.id)
    else:
        form = StoreForm(instance=store)

    return render(request, 'stores/edit_store.html', {'form': form, 'store': store})

@login_required
@store_access_required
def delete_store(request, store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)

    if request.method == 'POST':
        store.delete()
        return redirect('store_list')

    return render(request, 'stores/delete_store.html', {'store': store})

@login_required
@store_access_required
def add_store_member(request, store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)

    if request.method == 'POST':
        form = StoreMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.store = store
            member.save()
            return redirect('store_detail', store_id=store.id)
    else:
        form = StoreMemberForm()

    return render(request, 'stores/add_store_member.html', {
        'form': form,
        'store': store
    })
