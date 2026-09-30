from datetime import datetime

from s3mapgen.application.shell.foundation import default_seed_value


def test_default_seed_uses_the_current_date_and_hour():
    first = default_seed_value(datetime(2026, 8, 19, 1, 12))
    later_same_hour = default_seed_value(datetime(2026, 8, 19, 1, 58))
    next_hour = default_seed_value(datetime(2026, 8, 19, 2, 0))

    assert first == "2026081901"
    assert later_same_hour == first
    assert next_hour == "2026081902"
