from pynput import keyboard, mouse
from typing import Dict


class InputHandler:
    def __init__(self) -> None:
        self.keys: Dict[str, bool] = {}
        self.mouse_buttons: Dict[str, bool] = {}
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press, on_release=self.on_key_release
        )
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def on_key_press(self, key: keyboard.Key) -> None:
        self.keys[str(key)] = True

    def on_key_release(self, key: keyboard.Key) -> None:
        self.keys[str(key)] = False

    def on_mouse_click(self, x, y, button, pressed) -> None:
        self.mouse_buttons[str(button)] = pressed

    def is_key_pressed(self, key: str) -> bool:
        return self.keys.get(key, False)

    def is_mouse_button_pressed(self, button: str) -> bool:
        return self.mouse_buttons.get(button, False)

    def handle_input(self) -> None:
        # Logic to handle input events
        pass

    def stop(self) -> None:
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
