import hmac
import hashlib
from common.redis_client import redis_client

WEBHOOK_TTL = 60 * 60

def verify_github_signature(secret: str, body: bytes, signature_header: str) -> bool:
    if not signature_header:
        return False

    sha_name, signature = signature_header.split("=")
    if sha_name != "sha256":
        return False

    mac = hmac.new(
        secret.encode(),
        msg=body,
        digestmod=hashlib.sha256
    )

    return hmac.compare_digest(mac.hexdigest(), signature)
def is_duplicate_event(event_id: str) -> bool:
    key = f"github_event:{event_id}"
    created = redis_client.set(key, "processed", nx=True, ex=WEBHOOK_TTL)
    return created is None