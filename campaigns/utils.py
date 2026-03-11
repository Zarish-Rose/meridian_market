from subscribers.models import Subscriber
from .services.messaging import send_whatsapp_message

def send_campaign(campaign):
    subscribers = campaign.store.subscribers.all()

    for s in subscribers:
        if campaign.message_type in ['whatsapp', 'all']:
            send_whatsapp_message(s, campaign.message)

        # Existing email/SMS logic goes here

    campaign.sent = True
    campaign.save()
