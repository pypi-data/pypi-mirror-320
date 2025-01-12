from pynput import keyboard
from typing import Dict


class InputHandler:
    class Key:
        SPACE: str = "SPACE"
        LEFT: str = "LEFT"
        RIGHT: str = "RIGHT"
        A: str = "A"
        B: str = "B"
        C: str = "C"
        D: str = "D"
        E: str = "E"
        F: str = "F"
        G: str = "G"
        H: str = "H"
        I: str = "I"
        J: str = "J"
        K: str = "K"
        L: str = "L"
        M: str = "M"
        N: str = "N"
        O: str = "O"
        P: str = "P"
        Q: str = "Q"
        R: str = "R"
        S: str = "S"
        T: str = "T"
        U: str = "U"
        V: str = "V"
        W: str = "W"
        X: str = "X"
        Y: str = "Y"
        Z: str = "Z"
        ESCAPE: str = "ESCAPE"
        ENTER: str = "ENTER"
        TAB: str = "TAB"
        BACKSPACE: str = "BACKSPACE"
        SHIFT: str = "SHIFT"
        CTRL: str = "CTRL"
        ALT: str = "ALT"
        CAPS_LOCK: str = "CAPS_LOCK"
        NUM_LOCK: str = "NUM_LOCK"
        SCROLL_LOCK: str = "SCROLL_LOCK"
        INSERT: str = "INSERT"
        DELETE: str = "DELETE"
        HOME: str = "HOME"
        END: str = "END"
        PAGE_UP: str = "PAGE_UP"
        PAGE_DOWN: str = "PAGE_DOWN"
        ARROW_UP: str = "ARROW_UP"
        ARROW_DOWN: str = "ARROW_DOWN"
        ARROW_LEFT: str = "ARROW_LEFT"
        ARROW_RIGHT: str = "ARROW_RIGHT"
        F1: str = "F1"
        F2: str = "F2"
        F3: str = "F3"
        F4: str = "F4"
        F5: str = "F5"
        F6: str = "F6"
        F7: str = "F7"
        F8: str = "F8"
        F9: str = "F9"
        F10: str = "F10"
        F11: str = "F11"
        F12: str = "F12"

    def __init__(self) -> None:
        self.keys: Dict[str, bool] = {
            key: False for key in dir(self.Key) if not key.startswith("__")
        }
        self.listener: keyboard.Listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.listener.start()

    def on_press(self, key: keyboard.Key) -> None:
        try:
            self.keys[key.char.upper()] = True
        except AttributeError:
            self.keys[str(key).upper()] = True

    def on_release(self, key: keyboard.Key) -> None:
        try:
            self.keys[key.char.upper()] = False
        except AttributeError:
            self.keys[str(key).upper()] = False

    def _is_key_pressed(self, key: str) -> bool:
        return self.keys.get(key.upper(), False)

    def handle_input(self, key: str) -> bool:
        return self._is_key_pressed(key)

    def stop(self) -> None:
        self.listener.stop()
