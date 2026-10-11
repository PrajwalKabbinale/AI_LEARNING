"""Smoke test: call each function in helper_functions.py (no LLM)."""

from helper_functions import generate_password, get_current_time, roll_dice

print(get_current_time())
print(roll_dice())
print(generate_password())
