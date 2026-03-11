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

@login_required
@store_access_required
def edit_subscriber(request, store_id, subscriber_id):
    store = Store.objects.get(id=store_id)
    subscriber = get_object_or_404(Subscriber, id=subscriber_id, store=store)

    if request.method == 'POST':
        form = SubscriberForm(request.POST, instance=subscriber)
        if form.is_valid():
            form.save()
            return redirect('subscriber_list', store_id=store.id)
    else:
        form = SubscriberForm(instance=subscriber)

    return render(request, 'subscribers/edit_subscriber.html', {
        'store': store,
        'form': form,
        'subscriber': subscriber
    })

@login_required
@store_access_required
def delete_subscriber(request, store_id, subscriber_id):
    store = Store.objects.get(id=store_id)
    subscriber = get_object_or_404(Subscriber, id=subscriber_id, store=store)

    if request.method == 'POST':
        subscriber.delete()
        return redirect('subscriber_list', store_id=store.id)

    return render(request, 'subscribers/delete_subscriber.html', {
        'store': store,
        'subscriber': subscriber
    })
