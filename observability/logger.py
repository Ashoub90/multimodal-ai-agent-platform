"""Logging and metrics setup.

Configure structured logging, OpenTelemetry, and other observability
instrumentation here.
"""

import logging


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    # further configuration (handlers, formatters, etc.)
