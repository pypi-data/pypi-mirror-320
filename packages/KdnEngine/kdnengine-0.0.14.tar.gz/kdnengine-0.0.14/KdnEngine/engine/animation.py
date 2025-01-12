from typing import List


class AnimationSystem:
    def __init__(self) -> None:
        self.animations: List[object] = []

    def update(self) -> None:
        for animation in self.animations:
            animation.update()
