from typing import List


class ScriptingEngine:
    def __init__(self) -> None:
        self.scripts: List[object] = []

    def add_script(self, script: object) -> None:
        self.scripts.append(script)

    def execute(self) -> None:
        for script in self.scripts:
            script.run()
