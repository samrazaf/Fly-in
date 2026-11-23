# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  parsing.py                                        :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: samrazaf <samrazaf@student.42antananari   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/11/17 15:54:19 by samrazaf        #+#    #+#               #
#  Updated: 2026/11/23 17:13:55 by samrazaf        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from pydantic import BaseModel, ValidationError, Field
from typing import Annotated
import pathlib
import regex as re


class ParseError(Exception):
    def __init__(self, msg="Invalid data"):
        pass


class ValidatorParserDrone(BaseModel):
    drone: Annotated[str, Field(pattern=(
        r"^nb_drones:"
        r"\x20"
        r"(?:[+])?\d+"
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


class Parsing:
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
        avalaible = ["nb_drones", "start_hub", "end_hub"]
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
        new_line = line
        if re.search(r"#", line):
            new_line = line.split("#")[0]
        value = re.findall(r"\d+\x20\d+", new_line)
        hub_pos = re.findall(r"^[^#].+:\x20.+(\d+\x20\d+)", data, re.MULTILINE)
        set_val = set(value)
        set_hub = set(hub_pos)
        if set_val != set_val:
            diff = set_val - set_hub
            raise ParseError(f"[ERROR] of line {number}")
        print(hub_pos)

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
        hub = re.findall(r"^(hub|start_hub|end_hub):\x20(\w+[^\s])", data, re.MULTILINE)
        value: list[str] = []
        for i in hub:
            _, y = i
            value.append(y)
        kevin = re.findall(r"(\w+)-(\w+)", line)
        for j in kevin:
            a, b = j
            if a not in value or b not in value:
                raise ParseError(f"[ERROR] in line {number} == invalid"
                                 f" or indefined hub name {line!r}")

    def primary_check_data(self, data,
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
                elif new_line.startswith(hub_type):
                    valid_hub(hub=line)
                    self.check_hub(new_line, number)
                    self.check_zone(new_line, number)
                    self.check_duplicate_pos(new_line, number)
                    #self.pick_data_hub(line)
                else:
                    raise ParseError(f"[ERROR] of line: {number} == unknown"
                                     f" type of line '{line}'")
            except ValidationError as error:
                raise ParseError(f"[ERROR] of line: {number} == invalid"
                                 f" format: {line!r}") from error
        return True

    def pick_all_data(self, data: str) -> tuple[str, list[str], list[str]]:
        nb_drones: str = ""
        connection: list[str] = []
        hub: list[str] = []
        inventory = {}
        for line in data.splitlines():
            line = line.strip()
            if line == "" or line.startswith('#'):
                continue
            if line.startswith("nb_drones:"):
                new = line.split(":")
                inventory[new[0]] = new[1].strip()
            elif line.startswith("connection:"):
                new = line.split(" ")
                print(new)
                #inventory[new[1].strip] = tuple(int(new[2]), int(new[3]), new[4].strip())
            else:
                hub.append(line)
        return inventory

    #def pick_data_hub(self, line: list[str]) -> tuple[str, str, int, int, str, str, int]:
    #    data = line.split(' ')[1:]
    #    print(data)


if __name__ == "__main__":
    try:
        test = Parsing()
        valid_drone = ValidatorParserDrone
        valid_hub = ValidatorParserHub
        valid_connection = ValidatorParserConnection
        data = test.read_file("config.txt")
        test.primary_check_data(data, valid_drone, valid_hub, valid_connection)
        #value = test.pick_all_data(data)
        #print(value)
    except BaseException as error:
        print(error)
