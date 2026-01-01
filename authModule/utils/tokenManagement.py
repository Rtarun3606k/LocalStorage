import json
import time
from encryption.enc import encrypt, decrypt
from utils.kerberosUtils import is_expired


# -------------------------------
# Ticket Creation
# -------------------------------

def create_tgt(user_id, session_key, expires_in=3600):
    payload = {
        "type": "TGT",
        "user_id": user_id,
        "session_key": session_key,
        "exp": time.time() + expires_in
    }
    return encrypt(json.dumps(payload))


def create_service_ticket(user_id, service, session_key, expires_in=600):
    payload = {
        "type": "SERVICE",
        "user_id": user_id,
        "service": service,
        "session_key": session_key,
        "exp": time.time() + expires_in
    }
    return encrypt(json.dumps(payload))


# -------------------------------
# Ticket Validation
# -------------------------------

def validate_tgt(tgt):
    try:
        data = json.loads(decrypt(tgt))
        if data["type"] != "TGT":
            return None
        if is_expired(data["exp"]):
            return None
        return data
    except Exception:
        return None


def validate_service_ticket(ticket, expected_service):
    try:
        data = json.loads(decrypt(ticket))
        if data["type"] != "SERVICE":
            return None
        if data["service"] != expected_service:
            return None
        if is_expired(data["exp"]):
            return None
        return data
    except Exception:
        return None
