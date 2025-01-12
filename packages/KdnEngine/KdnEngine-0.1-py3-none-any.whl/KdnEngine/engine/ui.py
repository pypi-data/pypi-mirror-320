from typing import List


class UIManager:
    def __init__(self) -> None:
        self.elements: List[object] = []

    def render(self) -> None:
        for element in self.elements:
            element.render()
        # Add UI rendering logic here


# Instructions:
# - This file handles UI rendering.
# - Implement UI rendering logic and integrate with the game loop.
