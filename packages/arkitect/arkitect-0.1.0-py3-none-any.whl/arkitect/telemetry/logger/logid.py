import random
from datetime import datetime

time_fmt = "%Y%m%d%H%M%S"


def gen_log_id() -> str:
    """
    Generates a unique log ID.

    This function creates a log ID by combining
    the current date and time with a random number.
    The date and time are formatted as YYYYMMDDHHMMSS,
    and the random number is a 20-digit hexadecimal number.
    """
    return datetime.now().strftime(time_fmt) + format(
        random.randint(0, 2**64 - 1), "020X"
    )
