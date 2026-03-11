from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from stores.decorators import store_access_required
from stores.models import Store
from .models import Subscriber
from .forms import SubscriberForm

@login_required
@store_access_required
def subscriber_list(request, store_id):
    store = Store.objects.get(id=store_id)
    subscribers = store.subscribers.all()
    return render(request, 'subscribers/subscriber_list.html', {
        'store': store,
        'subscribers': subscribers
    })

@login_required
@store_access_required
def add_subscriber(request, store_id):
    store = Store.objects.get(id=store_id)

    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            subscriber = form.save(commit=False)
            subscriber.store = store
            subscriber.save()
            return redirect('subscriber_list', store_id=store.id)
    else:
        form = SubscriberForm()

    return render(request, 'subscribers/add_subscriber.html', {
        'store': store,
        'form': form
    })
