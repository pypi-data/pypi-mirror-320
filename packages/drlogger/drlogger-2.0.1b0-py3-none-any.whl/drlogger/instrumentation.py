"""instrumentation.py"""

try:
    from opentelemetry.trace import get_current_span # pylint: disable=unused-import
except ModuleNotFoundError:
    def get_current_span() -> None:
        """dummy current span"""
