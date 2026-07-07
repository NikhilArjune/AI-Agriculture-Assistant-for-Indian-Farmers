import logging
import sys

from core.config import settings


def setup_logging() -> None:
    level = logging.DEBUG if settings.debug else logging.INFO

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=date_fmt,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Silence noisy third-party loggers
    for noisy in ("httpx", "httpcore", "motor", "pymongo"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
