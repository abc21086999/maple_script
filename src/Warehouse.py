from src.MapleScript import MapleScript
from src.ConfigLoader import YamlLoader


class Warehouse(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)
        self.__number_dict = self.yaml_loader.warehouse_dict
