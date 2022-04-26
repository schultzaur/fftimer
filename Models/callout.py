from dataclasses import dataclass

@dataclass()
class Callout:
    timestamp: float
    description: str
    active: bool
    notes: str
    screen_image_path: str
    cast_image_path: str