from typing import List
import dearpygui.dearpygui as dpg


class UIManager:
    def __init__(self) -> None:
        self.elements: List[object] = []
        dpg.create_context()

    def add_element(self, element: object) -> None:
        self.elements.append(element)

    def render(self) -> None:
        dpg.create_viewport(title="KdnEngine UI", width=1200, height=800)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        with dpg.window(label="Main Window"):
            for element in self.elements:
                element.render()

        dpg.start_dearpygui()
        dpg.destroy_context()
