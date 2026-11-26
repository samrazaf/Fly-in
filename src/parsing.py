# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  parsing.py                                        :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: samrazaf <samrazaf@student.42antananari   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/11/17 15:54:19 by samrazaf        #+#    #+#               #
#  Updated: 2026/11/26 14:26:08 by samrazaf        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from pydantic import BaseModel, ValidationError, Field
from typing import Annotated, TypedDict
import pathlib
import re


class HubOptions(TypedDict, total=False):
    zone: str
    color: str
    max_drones: int


class HubInfo(TypedDict, total=False):
    type: str
    x: int
    y: int
    options: HubOptions


class ConnectionInfo(TypedDict, total=False):
    a: str
    b: str
    capacity: int


class Inventory(TypedDict, total=False):
    nb_drones: int
    hubs: dict[str, HubInfo]
    connections: list[ConnectionInfo]


class ParseError(Exception):
    def __init__(self, msg="Invalid data"):
        super().__init__(msg)


class ValidatorParserDrone(BaseModel):
    drone: Annotated[str, Field(pattern=(
        r"^nb_drones:"
        r"\x20"
        r"(?:[+])?0*[1-9]\d*"
        r"(?:\s*#+.*)?$"
    ))]


class ValidatorParserHub(BaseModel):
    hub: Annotated[str,
                   Field(pattern=(
                      r"^(?:start_hub|hub|end_hub):"
                      r"\x20"
                      r"[^-\x20]+"
                      r"\x20"
                      r"(?:[+-])?\d+"
                      r"\x20"
                      r"(?:[+-])?\d+"
                      r"(?:\s*#+.*|"
                      r"(?:"
                      r"\x20"
                      r"\["
                      r"(?:zone=[a-zA-Z_]+"
                      r"|color=[^\W\d]+"
                      r"|max_drones=\d+)"
                      r"(?:\x20(?:zone=[a-zA-Z_]+"
                      r"|color=[^\W\d]+"
                      r"|max_drones=\d+)){0,2}"
                      r"\](?:\s*#+.*)?"
                      r")?)$"
                      ))]


class ValidatorParserConnection(BaseModel):
    connection: Annotated[str,
                          Field(pattern=(
                              r"^connection:\x20"
                              r"[^-\s]+"
                              r"-"
                              r"[^\s-]+"
                              r"(?:\s*#+.*|"
                              r"(?:"
                              r"\x20"
                              r"\["
                              r"max_link_capacity=\d+"
                              r"\](?:\s*#+.*)?"
                              r")?)$"
                              ))]


class ParsingValidator:
    def read_file(self, path: str | pathlib.Path) -> str:
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = file.read()
            return data
        except OSError as error:
            raise ParseError(f"[ERROR] : {error}")

    def check_line(self, data: str) -> bool:
        s = []
        for number, line in enumerate(data.splitlines(), start=1):
            line = line.strip()
            if line == "" or line.startswith('#'):
                continue
            s.append(line)
            if s[0]:
                first_line = s[0]
                if first_line.startswith("nb_drones:"):
                    return True
                else:
                    raise ParseError(f"[ERROR] of line {number} == "
                                     "first line must be "
                                     "define NUMBER OF DRONES")
        return False

    def check_duplicate_line(self, data) -> bool:
        inventory = {}
        avalaible = ["nb_drones", "start_hub", "end_hub"]
        for number, line in enumerate(data.splitlines(), start=1):
            line = line.strip()
            if line == "" or line.startswith('#'):
                continue
            if line.startswith(avalaible[0] + ':'):
                inventory[number] = line.split(':')[0]
            if line.startswith(avalaible[1] + ':'):
                inventory[number] = line.split(':')[0]
            if line.startswith(avalaible[2] + ':'):
                inventory[number] = line.split(':')[0]
        if len(inventory) > 3:
            x, y, z = 0, 0, 0
            for value, num in inventory.items():
                if value == avalaible[0]:
                    x += 1
                if value == avalaible[1]:
                    y += 1
                if value == avalaible[2]:
                    z += 1
            reps = max(x, y, z)
            if reps == x:
                check = avalaible[0]
            elif reps == y:
                check = avalaible[1]
            elif reps == z:
                check = avalaible[2]
            num = [
                number for number, value in inventory.items()
                if value == check
            ]
            num = str(num)
            num = num.replace(',', ' and').replace('[', "").replace(']', '')
            raise ParseError(f"[ERROR] REBOUND of '{check}' in line "
                             f"{num}")
        return True

    def check_peak_hub(self, data: str) -> bool:
        inventory = []
        avalaible = ["nb_drones", "start_hub", "end_hub", "connection"]
        for line in data.splitlines():
            line = line.strip()
            if line == "" or line.startswith('#'):
                continue
            if line.startswith(avalaible[0] + ':'):
                inventory.append(line.split(':')[0])
            if line.startswith(avalaible[1] + ':'):
                inventory.append(line.split(':')[0])
            if line.startswith(avalaible[2] + ':'):
                inventory.append(line.split(':')[0])
            if line.startswith(avalaible[3] + ':'):
                inventory.append(line.split(':')[0])
        set_inv = set(inventory)
        set_ava = set(avalaible)
        if set_inv != set_ava:
            diff = set_ava - set_inv
            raise ParseError(f"[ERROR] {diff} is not defined")
        return True

    def check_hub(self, data: str, number: int) -> bool:
        new_data = data
        if re.search(r"#", data):
            new_data = data.split("#")[0]
        value = re.findall(r"(zone|color|max_drones)=", new_data)
        check = set(value)
        if len(value) != len(check):
            raise ParseError(f"[ERROR] of line {number} == Meta"
                             f" data REBOUND: '{data}'")
        return True

    def check_duplicate_pos(self, data: str, line: str, number: int) -> bool:
        hub_pos = re.findall(r"^(hub|start_hub|end_hub):"
                             r"\x20[^-\x20]+\x20(\d+\x20\d+)",
                             data, re.MULTILINE)
        line_pos = re.findall(r"^(hub|start_hub|end_hub):"
                              r"\x20[^-\x20]+\x20(\d+\x20\d+)", line)
        count = 0
        for new_pos in hub_pos:
            if new_pos in line_pos:
                count += 1
        if count > 1:
            raise ParseError(f"[ERROR] of line {number} == Position"
                             f" data REBOUND: {line}")
        return True

    def check_zone(self, data: str, number: int) -> bool:
        if re.findall(r"(zone)", data):
            pass
        else:
            return True
        if re.findall(r"(zone=(restricted|normal|blocked|priority))", data):
            return True
        else:
            raise ParseError(f"[ERROR] of line {number} =="
                             f" unknown zone type: {data!r}")

    def check_connection(self, data: str, line: str, number: int) -> bool:
        hub = re.findall(r"^(hub|start_hub|end_hub):"
                         r"\x20(\w+[^\s])", data, re.MULTILINE)
        value: list[str] = []
        for i in hub:
            _, y = i
            value.append(y)
        hub_connection = re.findall(r"^connection:\x20"
                                    r"([^-\20].*)-([\S]+)", line)
        for hub_value in hub_connection:
            a, b = hub_value
            if a not in value or b not in value:
                raise ParseError(f"[ERROR] in line {number} == invalid"
                                 f" or indefined hub name {line!r}")
        return True

    def check_duplicate_connection(self, data: str, line: str,
                                   number: int) -> bool:
        connection = re.findall(r"^connection:\x20([^-\x20].*)"
                                r"-([\S]+)", data, re.MULTILINE)
        connection_line = re.findall(r"^connection:\x20([^-\x20].*)"
                                     r"-([\S]+)", line)
        count: int = 0
        x, y = connection_line[0]
        if x == y:
            raise ParseError(f"[ERROR] in line {number} == connection"
                             f" rebound in one zone {line!r}")
        for connex in connection:
            prim, second = connex
            if ((str(prim)+str(second) == str(x)+str(y))
               or str(prim)+str(second) == str(y)+str(x)):
                count += 1
        if count > 1:
            raise ParseError(f"[ERROR] in line {number} == connection"
                             f" rebound in two zone {line!r}")
        return True

    def check_duplicate_hub_name(self, data: str) -> bool:
        names = re.findall(r"^(hub|start_hub|end_hub):\x20([\S]+)",
                           data, re.MULTILINE)
        list_name = []
        value = []
        for name in names:
            _, hub_name = name
            list_name.append(hub_name)
        set_hub_name = set(list_name)
        list_hub = list(set_hub_name)
        if len(set_hub_name) != len(list_name):
            diff = [x for x in list_hub if list_name.count(x) > 1]
            for number, line in enumerate(data.splitlines(), start=1):
                new_line = line.strip()
                if new_line == "" or new_line.startswith('#'):
                    continue
                if re.findall(r"^(?:hub|start_hub|end_hub):"
                              rf"\x20{re.escape(diff[0])}",
                              line) != []:
                    value.append(number)
            string = (str(value).replace("[", "")
                      .replace("]", "").replace(",", " and"))
            if value != []:
                raise ParseError(f"[ERROR] in line {string} =="
                                 f" name of hub rebound '{diff[0]}'")
        return True

    def check_data(self, data: str,
                   valid_drones: type[ValidatorParserDrone],
                   valid_hub: type[ValidatorParserHub],
                   valid_connection: type[ValidatorParserConnection]
                   ) -> bool:
        if data == "":
            raise ParseError("Data invalid")

        hub_type = ("start_hub", "end_hub", "hub")

        if self.check_line(data):
            pass

        if self.check_peak_hub(data):
            pass

        if self.check_duplicate_line(data):
            pass

        if self.check_duplicate_hub_name(data):
            pass

        for number, line in enumerate(data.splitlines(), start=1):
            new_line = line.strip()
            if new_line == "" or new_line.startswith('#'):
                continue
            try:
                if new_line.startswith("nb_drones:"):
                    valid_drones(drone=line)
                elif new_line.startswith("connection:"):
                    valid_connection(connection=line)
                    self.check_connection(data, line, number)
                    self.check_duplicate_connection(data, line, number)
                elif new_line.startswith(hub_type):
                    valid_hub(hub=line)
                    self.check_hub(line, number)
                    self.check_zone(line, number)
                    self.check_duplicate_pos(data, line, number)
                else:
                    raise ParseError(f"[ERROR] of line: {number} == unknown"
                                     f" type of line '{line}'")
            except ValidationError as error:
                raise ParseError(f"[ERROR] of line: {number} == invalid"
                                 f" format: {line!r}") from error
        return True



class ParsingData:
    def pick_data(self, data: str) -> Inventory:
        hub_re = re.compile(
            r"(?P<type>hub|start_hub|end_hub):\x20"
            r"(?P<name>[^-\x20]+)\x20"
            r"(?P<x>(?:[-+])?\d+)\x20"
            r"(?P<y>(?:[-+])?\d+)"
            r"(?:\x20\["
            r"(?P<option>[^\]]+)"
            r"\])?"
        )

        connection_re = re.compile(
            r"connection:\x20"
            r"(?P<a>[^-\x20]+)-"
            r"(?P<b>[\S]+)"
            r"(?:\x20\["
            r"max_link_capacity="
            r"(?P<capacity>\d+)"
            r"\])?"
        )

        option_re = re.compile(
            r"(?P<key>zone|color|max_drones)="
            r"(?P<value>[^\x20]+)"
        )

        hub_type = ("start_hub", "end_hub", "hub")
        inventory: Inventory = {}
        hub_name: dict[str, HubInfo] = {}
        connection: list[ConnectionInfo] = []
        for line in data.splitlines():
            new_line = line.strip()

            if new_line == "" or new_line.startswith('#'):
                continue

            if new_line.startswith("nb_drones:"):
                nb = new_line.split(':')
                inventory[nb[0].strip()] = int(nb[1].strip())

            elif new_line.startswith("connection:"):
                connex = connection_re.search(new_line)
                group_connex: dict[str, str|int] = {}
                group_connex['a'] = connex.group("a")
                group_connex['b'] = connex.group("b")

                if connex.group("capacity"):
                    group_connex['capacity'] = int(connex.group("capacity"))
                else:
                    group_connex['capacity'] = 1

                connection.append(group_connex)

            elif new_line.startswith(hub_type):
                hub = hub_re.search(new_line)

                option_value: dict[str, str|int] = {}
                if hub.group("option"):
                    for params in option_re.finditer(hub.group("option")):
                        key = params.group("key")
                        value = params.group("value")
                        option_value[key] = value

                if "zone" not in option_value.keys():
                    option_value['zone'] = "normal"
                if "color" not in option_value.keys():
                    option_value['color'] = "none"
                if "max_drones" not in option_value.keys():
                    option_value['max_drones'] = 1

                hub_value: dict[str, int|str|dict[str, str|int]] = {}
                hub_value['type'] = hub.group("type")
                hub_value['x'] = int(hub.group("x"))
                hub_value['y'] = int(hub.group("y"))
                hub_value['options'] = option_value

                hub_name[hub.group("name")] = hub_value

        inventory['hubs'] = hub_name
        inventory['connections'] = connection
        return inventory

if __name__ == "__main__":
    try:
        test = ParsingValidator()
        valid_drone = ValidatorParserDrone
        valid_hub = ValidatorParserHub
        valid_connection = ValidatorParserConnection
        data = test.read_file("config.txt")
        test2 = ParsingData()
        test.check_data(data, valid_drone, valid_hub, valid_connection)
        value = test2.pick_data(data)
        print(value)
    except BaseException as error:
        print(error)
