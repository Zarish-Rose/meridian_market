class WhatsAppProviderBase:
    """
    Base class for WhatsApp providers.
    All providers must implement the send_message method.
    """
    def send_message(self, to, message):
        raise NotImplementedError("send_message must be implemented by subclasses")

class DummyWhatsAppProvider(WhatsAppProviderBase):
    """
    Placeholder provider for development.
    Replace with Twilio or Meta provider later.
    """
    def send_message(self, to, message):
        print(f"[DEV] WhatsApp to {to}: {message}")
        return True
