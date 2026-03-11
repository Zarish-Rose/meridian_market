from .whatsapp import DummyWhatsAppProvider

def get_whatsapp_provider():
    # Later: read from settings or environment variables
    return DummyWhatsAppProvider()
