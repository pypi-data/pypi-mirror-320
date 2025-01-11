import logging


logger = logging.getLogger(__name__)


def configure_logging(level: int = logging.DEBUG) -> None:
    logging.basicConfig(
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='[%(asctime)s.%(msecs)03d] %(message)s',
    )
