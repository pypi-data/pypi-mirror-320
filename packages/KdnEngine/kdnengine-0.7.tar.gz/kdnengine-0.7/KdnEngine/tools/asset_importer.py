class AssetImporter:
    def __init__(self) -> None:
        self.assets = {}

    def import_asset(self, name: str, filepath: str) -> None:
        # Logic to import the asset from the given filepath
        self.assets[name] = filepath

    def get_asset(self, name: str) -> str:
        return self.assets.get(name)
