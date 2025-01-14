from ..layers import DataProcessing

class Configuration:
    def __init__(self, node_config: dict[str, any]):
        self.type = 'database'
        self.id = 'timescaledb'
        self.url = node_config['url']
        self.table_name = node_config['table_name']
        self.columns = node_config['columns']
        self.__set_layers()

    def __set_layers(self):
        self.data_processing = DataProcessing(self)