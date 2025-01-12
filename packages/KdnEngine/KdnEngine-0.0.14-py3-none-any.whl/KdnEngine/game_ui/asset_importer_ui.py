import dearpygui.dearpygui as dpg
from KdnEngine.tools.asset_importer import AssetImporter


class AssetImporterUI:
    def __init__(self, asset_importer: AssetImporter) -> None:
        self.asset_importer = asset_importer

    def render(self) -> None:
        dpg.add_text("Asset Importer")
        dpg.add_button(label="Import Asset", callback=self.import_asset)

    def import_asset(self) -> None:
        pass
