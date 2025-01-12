import dearpygui.dearpygui as dpg
from KdnEngine.tools.level_editor import LevelEditor


class LevelEditorUI:
    def __init__(self, level_editor: LevelEditor) -> None:
        self.level_editor = level_editor

    def render(self) -> None:
        dpg.add_text("Level Editor")
        dpg.add_button(label="Edit Level", callback=self.edit_level)

    def edit_level(self) -> None:
        pass
