from datetime import datetime
from utils.sorting import sort_todos, get_priority_label, get_priority_css_class, PRIORITY_ORDER


class MockTodo:
    def __init__(self, title, priority='none', deadline=None, created_at=None):
        self.title = title
        self.priority = priority
        self.deadline = deadline
        self.created_at = created_at or datetime(2026, 1, 1, 12, 0, 0)


def test_priority_order_high_before_medium():
    todos = [
        MockTodo('medium task', priority='medium'),
        MockTodo('high task', priority='high'),
    ]
    result = sort_todos(todos, 'priority', 'asc')
    assert result[0].priority == 'high'


def test_priority_order_full_sequence():
    todos = [
        MockTodo('none task', priority='none'),
        MockTodo('low task', priority='low'),
        MockTodo('high task', priority='high'),
        MockTodo('medium task', priority='medium'),
    ]
    result = sort_todos(todos, 'priority', 'asc')
    assert result[0].priority == 'high'
    assert result[1].priority == 'medium'
    assert result[2].priority == 'low'
    assert result[3].priority == 'none'


def test_sort_by_title_ascending():
    todos = [MockTodo('Zebra'), MockTodo('Apple'), MockTodo('Mango')]
    result = sort_todos(todos, 'title', 'asc')
    assert result[0].title == 'Apple'
    assert result[-1].title == 'Zebra'


def test_sort_by_title_descending():
    todos = [MockTodo('Apple'), MockTodo('Zebra')]
    result = sort_todos(todos, 'title', 'desc')
    assert result[0].title == 'Zebra'


def test_sort_by_created_ascending():
    todos = [
        MockTodo('newer', created_at=datetime(2026, 6, 1)),
        MockTodo('older', created_at=datetime(2026, 1, 1)),
    ]
    result = sort_todos(todos, 'created', 'asc')
    assert result[0].title == 'older'


def test_sort_by_created_descending():
    todos = [
        MockTodo('older', created_at=datetime(2026, 1, 1)),
        MockTodo('newer', created_at=datetime(2026, 6, 1)),
    ]
    result = sort_todos(todos, 'created', 'desc')
    assert result[0].title == 'newer'


def test_sort_by_deadline():
    todos = [
        MockTodo('later', deadline=datetime(2026, 12, 31)),
        MockTodo('sooner', deadline=datetime(2026, 6, 1)),
    ]
    result = sort_todos(todos, 'deadline', 'asc')
    assert result[0].title == 'sooner'


def test_sort_unknown_field_returns_original():
    todos = [MockTodo('task1'), MockTodo('task2')]
    result = sort_todos(todos, 'nonexistent', 'asc')
    assert len(result) == 2


def test_sort_empty_list():
    result = sort_todos([], 'priority', 'asc')
    assert result == []


def test_get_priority_label_all_values():
    assert get_priority_label('high') == 'High'
    assert get_priority_label('medium') == 'Medium'
    assert get_priority_label('low') == 'Low'
    assert get_priority_label('none') == '—'
    assert get_priority_label('invalid') == '—'


def test_get_priority_css_class():
    assert get_priority_css_class('high') == 'priority-high'
    assert get_priority_css_class('medium') == 'priority-medium'
    assert get_priority_css_class('low') == 'priority-low'
    assert get_priority_css_class('none') == ''


def test_priority_order_values():
    assert PRIORITY_ORDER['high'] < PRIORITY_ORDER['medium']
    assert PRIORITY_ORDER['medium'] < PRIORITY_ORDER['low']
    assert PRIORITY_ORDER['low'] < PRIORITY_ORDER['none']
