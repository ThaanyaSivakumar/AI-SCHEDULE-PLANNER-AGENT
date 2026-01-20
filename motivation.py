import random

TIPS = [
    "Small progress is still progress.",
    "Discipline beats motivation.",
    "Consistency creates success.",
    "Your future self will thank you.",
    "Start now. Improve later."
]

def get_tip():
    return random.choice(TIPS)
