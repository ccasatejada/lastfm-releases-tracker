from datetime import date, datetime

from utils.date_utils import compute_length, format_date, format_datetime


class TestFormatDatetime:
    def test_none_returns_empty_string(self):
        assert format_datetime(None) == ''

    def test_formats_correctly(self):
        assert format_datetime(datetime(2024, 3, 15, 10, 30)) == '2024-03-15 10:30'

    def test_formats_midnight(self):
        assert format_datetime(datetime(2024, 1, 1, 0, 0)) == '2024-01-01 00:00'


class TestFormatDate:
    def test_none_returns_empty_string(self):
        assert format_date(None) == ''

    def test_formats_correctly(self):
        assert format_date(date(2024, 3, 15)) == '2024-03-15'


class TestComputeLength:
    def test_zero(self):
        assert compute_length(0) == (0, 0)

    def test_exact_minutes(self):
        assert compute_length(120) == (2, 0)

    def test_minutes_and_seconds(self):
        assert compute_length(90) == (1, 30)

    def test_large_value(self):
        mins, secs = compute_length(3661)
        assert mins == 61
        assert secs == 1
