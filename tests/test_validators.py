from utils.validators import (
    validate_priority, validate_title, validate_direction,
    validate_sort_by, validate_email, validate_description
)


def test_validate_priority_valid_values():
    for p in ['none', 'low', 'medium', 'high']:
        assert validate_priority(p) == p


def test_validate_priority_invalid_returns_none():
    assert validate_priority('urgent') == 'none'
    assert validate_priority('CRITICAL') == 'none'
    assert validate_priority('') == 'none'


def test_validate_priority_none_input():
    assert validate_priority(None) == 'none'


def test_validate_title_valid():
    assert validate_title('Buy milk') == 'Buy milk'
    assert validate_title('  trimmed  ') == 'trimmed'


def test_validate_title_empty_returns_none():
    assert validate_title('') is None
    assert validate_title('   ') is None
    assert validate_title(None) is None


def test_validate_title_truncates_long_input():
    long = 'x' * 300
    result = validate_title(long)
    assert len(result) == 200


def test_validate_direction_valid():
    assert validate_direction('asc') == 'asc'
    assert validate_direction('desc') == 'desc'


def test_validate_direction_invalid():
    assert validate_direction('up') == 'asc'
    assert validate_direction('') == 'asc'
    assert validate_direction(None) == 'asc'


def test_validate_sort_by_valid():
    for f in ['priority', 'deadline', 'created', 'title']:
        assert validate_sort_by(f) == f


def test_validate_sort_by_invalid():
    assert validate_sort_by('random') == 'priority'
    assert validate_sort_by('') == 'priority'


def test_validate_email_valid():
    assert validate_email('user@example.com') == 'user@example.com'
    assert validate_email('  USER@EXAMPLE.COM  ') == 'user@example.com'


def test_validate_email_no_at_sign():
    assert validate_email('notanemail') is None


def test_validate_email_empty():
    assert validate_email('') is None
    assert validate_email(None) is None


def test_validate_description_truncates():
    long = 'a' * 3000
    assert len(validate_description(long)) == 2000
