import dearpygui.dearpygui as dpg
from KdnEngine.engine.scene import SceneManager


class SceneManagerUI:
    def __init__(self, scene_manager: SceneManager) -> None:
        self.scene_manager = scene_manager

    def render(self) -> None:
        dpg.add_text("Scene Manager")
        dpg.add_button(label="Add Object", callback=self.add_object)

    def add_object(self) -> None:
        pass
