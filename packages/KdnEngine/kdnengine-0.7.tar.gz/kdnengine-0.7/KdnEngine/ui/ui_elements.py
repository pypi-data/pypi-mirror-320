import dearpygui.dearpygui as dpg


class UIButton:
    def __init__(self, label: str, callback: callable) -> None:
        self.label = label
        self.callback = callback

    def render(self) -> None:
        dpg.add_button(label=self.label, callback=self.callback)


class UILabel:
    def __init__(self, text: str) -> None:
        self.text = text

    def render(self) -> None:
        dpg.add_text(self.text)
