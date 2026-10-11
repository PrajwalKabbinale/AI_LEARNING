"""Local helper functions used by tool_functions_2.py (keyword shortcuts, no OpenAI tools API yet)."""

from datetime import datetime
import random


def get_current_time():
    """Return the current date and time."""
    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")


def roll_dice():
    """Return a random number between 1 and 6."""
    return random.randint(1, 6)
