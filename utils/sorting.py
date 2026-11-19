from datetime import datetime

PRIORITY_ORDER = {'high': 0, 'medium': 1, 'low': 2, 'none': 3}


def sort_todos(todos, sort_by, direction='asc'):
    try:
        if sort_by == 'priority':
            key = lambda t: (PRIORITY_ORDER.get(t.priority or 'none', 3), t.created_at or datetime.min)
            return sorted(todos, key=key, reverse=(direction == 'desc'))
        elif sort_by == 'deadline':
            return sorted(todos, key=lambda t: t.deadline or datetime.max, reverse=(direction == 'desc'))
        elif sort_by == 'created':
            return sorted(todos, key=lambda t: t.created_at or datetime.min, reverse=(direction == 'desc'))
        elif sort_by == 'title':
            return sorted(todos, key=lambda t: t.title.lower(), reverse=(direction == 'desc'))
        return todos
    except:
        return todos


def get_priority_label(priority):
    labels = {'high': 'High', 'medium': 'Medium', 'low': 'Low', 'none': '—'}
    return labels.get(priority, '—')


def get_priority_css_class(priority):
    classes = {'high': 'priority-high', 'medium': 'priority-medium', 'low': 'priority-low'}
    return classes.get(priority, '')
