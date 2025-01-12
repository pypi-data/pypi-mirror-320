class LevelEditor:
    def __init__(self) -> None:
        self.levels = {}

    def create_level(self, name: str) -> None:
        # Logic to create a new level
        self.levels[name] = {}

    def edit_level(self, name: str, data: dict) -> None:
        # Logic to edit an existing level
        if name in self.levels:
            self.levels[name].update(data)

    def save_level(self, name: str, filepath: str) -> None:
        # Logic to save the level to a file
        if name in self.levels:
            with open(filepath, "w") as file:
                file.write(str(self.levels[name]))

    def load_level(self, filepath: str) -> None:
        # Logic to load a level from a file
        with open(filepath, "r") as file:
            level_data = file.read()
            # Assuming level_data is a dictionary in string format
            self.levels[filepath] = eval(level_data)
