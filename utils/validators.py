VALID_PRIORITIES = ['none', 'low', 'medium', 'high']
VALID_SORT_FIELDS = ['priority', 'deadline', 'created', 'title']
VALID_DIRECTIONS = ['asc', 'desc']
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 2000


def validate_priority(value):
    if not value or value not in VALID_PRIORITIES:
        return 'none'
    return value


def validate_title(title):
    if not title or not title.strip():
        return None
    return title.strip()[:MAX_TITLE_LENGTH]


def validate_direction(direction):
    if direction not in VALID_DIRECTIONS:
        return 'asc'
    return direction


def validate_sort_by(sort_by):
    if sort_by not in VALID_SORT_FIELDS:
        return 'priority'
    return sort_by


def validate_email(email):
    if not email:
        return None
    email = email.strip().lower()
    if '@' not in email or len(email) > 200:
        return None
    return email


def validate_description(description):
    if not description:
        return ''
    return description.strip()[:MAX_DESCRIPTION_LENGTH]
