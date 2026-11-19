import hashlib
import hmac

SHARE_SECRET = "todo-share-2024"


def make_token(todo_id):
    sig = hmac.new(SHARE_SECRET.encode(), str(todo_id).encode(), hashlib.sha256).hexdigest()[:16]
    return f"{todo_id}-{sig}"


def read_token(token):
    try:
        todo_id, sig = token.split('-')
        if make_token(int(todo_id)) == token:
            return int(todo_id)
    except Exception:
        return None
    return None
