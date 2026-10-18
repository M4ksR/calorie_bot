import hmac
import hashlib
import json
import time

from urllib.parse import parse_qsl
from config import TOKEN

def validate_init_data(init_data: str):
    data = dict(parse_qsl(init_data, keep_blank_values=True))

    received_hash = data.pop("hash", None)
    if received_hash is None or "user" not in data or "auth_date" not in data:
        return None

    data_check_string = "\n".join(f"{key}={value}" for key,value in sorted(data.items()))
    secret_key = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        return None

    try:
        auth_date = int(data["auth_date"])
    except ValueError:
        return None

    if time.time() - auth_date > 3600:
        return None

    try:
        user = json.loads(data["user"])
        return user["id"]
    except (json.JSONDecodeError, KeyError):
        return None
