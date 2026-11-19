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


def group_by_priority(todos):
    groups = {'high': [], 'medium': [], 'low': [], 'none': []}
    for todo in todos:
        key = todo.priority if todo.priority in groups else 'none'
        groups[key].append(todo)
    return groups


def split_completed(todos):
    active = [t for t in todos if not t.completed]
    done = [t for t in todos if t.completed]
    return active, done


def sort_and_group(todos, sort_by, direction='asc'):
    active, done = split_completed(todos)
    active_sorted = sort_todos(active, sort_by, direction)
    done_sorted = sort_todos(done, sort_by, direction)
    return active_sorted + done_sorted
