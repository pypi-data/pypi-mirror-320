from typing import List


class SceneManager:
    def __init__(self) -> None:
        self.objects: List[object] = []

    def update(self) -> None:
        for obj in self.objects:
            obj.update()
