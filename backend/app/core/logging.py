"""
Application-wide logging configuration.
"""
import logging
import sys


def setup_logging():
    """
    Configures the root logger for the application.

    This setup ensures that log messages are directed to standard output
    with a consistent format.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
