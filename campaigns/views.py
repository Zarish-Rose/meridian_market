from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from stores.decorators import store_access_required
from stores.models import Store
from .models import Campaign
from .forms import CampaignForm
from .utils import send_campaign

@login_required
@store_access_required
def campaign_list(request, store_id):
    store = Store.objects.get(id=store_id)
    campaigns = store.campaigns.all().order_by('-created_at')
    return render(request, 'campaigns/campaign_list.html', {
        'store': store,
        'campaigns': campaigns
    })

@login_required
@store_access_required
def create_campaign(request, store_id):
    store = Store.objects.get(id=store_id)

    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.store = store
            campaign.save()
            return redirect('campaign_list', store_id=store.id)
    else:
        form = CampaignForm()

    return render(request, 'campaigns/create_campaign.html', {
        'store': store,
        'form': form
    })

@login_required
@store_access_required
def send_campaign_view(request, store_id, campaign_id):
    store = Store.objects.get(id=store_id)
    campaign = get_object_or_404(Campaign, id=campaign_id, store=store)

    if request.method == 'POST':
        send_campaign(campaign)
        return redirect('campaign_list', store_id=store.id)

    return render(request, 'campaigns/send_campaign.html', {
        'store': store,
        'campaign': campaign
    })
