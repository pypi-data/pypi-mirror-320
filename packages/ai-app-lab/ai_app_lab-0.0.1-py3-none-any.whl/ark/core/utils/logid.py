import random
from datetime import datetime

time_fmt = "%Y%m%d%H%M%S"


def gen_log_id() -> str:
    return datetime.now().strftime(time_fmt) + format(
        random.randint(0, 2**64 - 1), "020X"
    )
