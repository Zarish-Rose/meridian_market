from django.db import models
from .crypto import encrypt_value, decrypt_value


class EncryptedCharField(models.CharField):
    """
    Stores AES-encrypted text in the database.
    Automatically decrypts on access.
    """

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt_value(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return encrypt_value(value)
    