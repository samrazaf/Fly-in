from src.parsing import (ParsingData, ParsingValidator,
                     ValidatorParserConnection,
                     ValidatorParserDrone,
                     ValidatorParserHub)

from src.parsing import Inventory


class HubData:
    def __init__(self, name: str, value: dict):
        self.name = name
        self.pos_x = value['x']
        self.pos_y = value['y']
        self.type = value['type']
        self.color = value['options']['color']
        self.zone = value['options']['zone']
        self.max_drones = value['options']['max_drones']


class Graph:
    def let_graph(self, data: Inventory) -> dict[tuple[str]]:
        connection = data["connections"]
        list_graph = {}
        for p, n in data['hubs'].items():
            summit = n['options']['color']
            for c in connection:
                if c['a'] == p:
                    summit = c['b'], n['options']['color']
            list_graph[p] = summit
        return list_graph









if __name__ == "__main__":
    try:
        test = ParsingValidator()
        #valid_drone = ValidatorParserDrone
        #valid_hub = ValidatorParserHub
        #valid_connection = ValidatorParserConnection
        data = test.read_file("config.txt")

        #test.check_data(data, valid_drone, valid_hub, valid_connection)
        test2 = ParsingData()
        value = test2.pick_data(data)
        ger = []
        for i, j in value['hubs'].items():
            k = HubData(i, j)
            ger.append(k)
        print([ger[i].pos_x for i in range(len(ger))])
        #test3 = Graph()
        #test3.let_graph(value)
    except BaseException as error:
        print(error)
