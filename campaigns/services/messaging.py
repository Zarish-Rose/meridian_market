from .providers import get_whatsapp_provider

def send_whatsapp_message(subscriber, message):
    provider = get_whatsapp_provider()

    if not subscriber.phone:
        return False

    return provider.send_message(
        to=subscriber.phone,
        message=message
    )
