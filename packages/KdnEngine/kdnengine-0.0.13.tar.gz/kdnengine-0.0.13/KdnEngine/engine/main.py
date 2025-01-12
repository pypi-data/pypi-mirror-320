from KdnEngine.engine.rendering import Renderer
from KdnEngine.engine.physics import PhysicsEngine
from KdnEngine.engine.audio import AudioEngine
from KdnEngine.engine.input import InputHandler
from KdnEngine.engine.scene import SceneManager
from KdnEngine.engine.scripting import ScriptingEngine
from KdnEngine.engine.ui import (
    UIManager,
    SceneManagerUI,
    AssetImporterUI,
    LevelEditorUI,
)
from KdnEngine.tools.asset_importer import AssetImporter
from KdnEngine.tools.level_editor import LevelEditor


class KdnEngine:
    def __init__(self) -> None:
        self.renderer: Renderer = Renderer()
        self.physics_engine: PhysicsEngine = PhysicsEngine()
        self.audio_engine: AudioEngine = AudioEngine()
        self.input_handler: InputHandler = InputHandler()
        self.scene_manager: SceneManager = SceneManager()
        self.scripting_engine: ScriptingEngine = ScriptingEngine()
        self.ui_manager: UIManager = UIManager()
        self.asset_importer: AssetImporter = AssetImporter()
        self.level_editor: LevelEditor = LevelEditor()

        self.ui_manager.add_element(SceneManagerUI(self.scene_manager))
        self.ui_manager.add_element(AssetImporterUI(self.asset_importer))
        self.ui_manager.add_element(LevelEditorUI(self.level_editor))

    def run(self) -> None:
        running: bool = True
        while running:
            self.input_handler.handle_input()
            self.physics_engine.update()
            self.renderer.render()
            self.audio_engine.update()
            self.scene_manager.update()
            self.scripting_engine.execute()
            self.ui_manager.render()


if __name__ == "__main__":
    engine: KdnEngine = KdnEngine()
    engine.run()
