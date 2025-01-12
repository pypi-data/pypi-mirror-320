from KdnEngine.engine.rendering import Renderer
from KdnEngine.engine.physics import PhysicsEngine
from KdnEngine.engine.audio import AudioEngine
from KdnEngine.engine.input import InputHandler
from KdnEngine.engine.scene import SceneManager


class KdnEngine:
    def __init__(self) -> None:
        self.renderer: Renderer = Renderer()
        self.physics_engine: PhysicsEngine = PhysicsEngine()
        self.audio_engine: AudioEngine = AudioEngine()
        self.input_handler: InputHandler = InputHandler()
        self.scene_manager: SceneManager = SceneManager()

    def run(self) -> None:
        running: bool = True
        while running:
            self.input_handler.handle_input()
            self.physics_engine.update()
            self.renderer.render()
            self.audio_engine.update()
            self.scene_manager.update()


if __name__ == "__main__":
    engine: KdnEngine = KdnEngine()
    engine.run()
