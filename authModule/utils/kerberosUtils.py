import os
import time
import secrets


def generate_session_key():
    """
    Generate a random symmetric session key (Kerberos-style).
    """
    return secrets.token_hex(32)


def is_expired(expiry_timestamp):
    return time.time() > expiry_timestamp
