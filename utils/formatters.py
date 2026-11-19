from datetime import datetime

PRIORITY_COLORS = {
    'high': ('#ffcccc', '#cc0000'),
    'medium': ('#fff3cc', '#996600'),
    'low': ('#ccffcc', '#006600'),
}

PRIORITY_LABELS = {
    'high': 'High',
    'medium': 'Medium',
    'low': 'Low',
    'none': '—',
}


def format_priority_label(priority):
    return PRIORITY_LABELS.get(priority or 'none', '—')


def format_priority_colors(priority):
    return PRIORITY_COLORS.get(priority, ('#e0e0e0', '#555'))


def format_deadline_display(deadline):
    if not deadline:
        return ''
    if isinstance(deadline, str):
        try:
            dt = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return deadline
    return deadline.strftime('%Y-%m-%d %H:%M')


def format_relative_time(dt):
    if not dt:
        return 'never'
    now = datetime.utcnow()
    diff = now - dt
    if diff.days > 365:
        return f'{diff.days // 365}y ago'
    if diff.days > 30:
        return f'{diff.days // 30}mo ago'
    if diff.days > 0:
        return f'{diff.days}d ago'
    hours = diff.seconds // 3600
    if hours > 0:
        return f'{hours}h ago'
    minutes = diff.seconds // 60
    if minutes > 0:
        return f'{minutes}m ago'
    return 'just now'


def format_assignee_display(email):
    if not email:
        return ''
    if '@' in email:
        return email.split('@')[0]
    return email


def format_todo_count(count):
    if count == 0:
        return 'No todos'
    if count == 1:
        return '1 todo'
    return f'{count} todos'
