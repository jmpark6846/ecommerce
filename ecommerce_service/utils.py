import time
import random

from django.conf import settings
import pendulum
from pendulum.datetime import DateTime


def get_now(tz=settings.TIME_ZONE) -> DateTime:
    """Get current pendulum datetime instance of default timezone

    Returns:
        DateTime
    """
    return pendulum.now(tz)


def generate_unique_id() -> str:
    """
    Time based unique_id Function
    {length: 14, unique_for: {years: 34}, time_resolution: 100ms}
    """
    return str((int(time.time() * 1000) & 0xffffffffff) * 100 + int(random.random() * 100))

