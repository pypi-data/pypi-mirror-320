from typing import Tuple
import pygame


class AudioEngine:
    def __init__(self) -> None:
        pygame.mixer.init()
        self.sounds = {}

    def load_sound(self, name: str, filepath: str) -> None:
        self.sounds[name] = pygame.mixer.Sound(filepath)

    def play_sound(self, name: str) -> None:
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def update(self) -> None:
        pass
