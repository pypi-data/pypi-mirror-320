from typing import List


class SceneManager:
    def __init__(self) -> None:
        self.objects: List[object] = []

    def add_object(self, obj: object) -> None:
        self.objects.append(obj)

    def update(self) -> None:
        for obj in self.objects:
            obj.update()
