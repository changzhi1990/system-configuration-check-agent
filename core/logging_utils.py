from __future__ import annotations

import logging


def configure_logging(verbose: bool = False) -> logging.Logger:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger("system-configuration-check-agent")


def get_logger() -> logging.Logger:
    return logging.getLogger("system-configuration-check-agent")
