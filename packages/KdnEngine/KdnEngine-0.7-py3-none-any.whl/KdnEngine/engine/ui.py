from typing import List
from KdnEngine.engine.scene import SceneManager
from KdnEngine.tools.asset_importer import AssetImporter
from KdnEngine.tools.level_editor import LevelEditor


class UIManager:
    def __init__(self) -> None:
        self.elements: List[object] = []

    def add_element(self, element: object) -> None:
        self.elements.append(element)

    def render(self) -> None:
        for element in self.elements:
            element.render()


class SceneManagerUI:
    def __init__(self, scene_manager: SceneManager) -> None:
        self.scene_manager = scene_manager

    def render(self) -> None:
        # Logic to render SceneManager UI
        pass


class AssetImporterUI:
    def __init__(self, asset_importer: AssetImporter) -> None:
        self.asset_importer = asset_importer

    def render(self) -> None:
        # Logic to render AssetImporter UI
        pass


class LevelEditorUI:
    def __init__(self, level_editor: LevelEditor) -> None:
        self.level_editor = level_editor

    def render(self) -> None:
        # Logic to render LevelEditor UI
        pass
