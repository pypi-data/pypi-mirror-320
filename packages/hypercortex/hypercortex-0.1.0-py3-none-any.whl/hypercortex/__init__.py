"""Nozzle package for testing and development utilities."""

def hello() -> str:
    """Return a greeting message.

    Returns:
        str: A hello message string.
    """
    return "Hello from nozzle! Testing if black formatting works correctly."

from .agents import hello_world_agent