# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  parsing.py                                        :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: samrazaf <samrazaf@student.42antananari   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/11/17 15:54:19 by samrazaf        #+#    #+#               #
#  Updated: 2026/11/17 17:15:18 by samrazaf        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from pydantic import BaseModel, Field
from typing import Annotated, Literal

class ParseError:
    def __init__(self, msg):
        pass

hub_type = Literal["start_hub:", "end_hub:"]

class ValidationParser(BaseModel):
    nb_drone: int = Field(gt=0)
    hub_peak: tuple[
        hub_type,
        str,
        int,
        int,
        Annotated[str, Field(pattern=r"^\[color=\S+\]$")]
    ]


#class Parsing:
#    def read_file(path):
#        with open(path, "r", encoding="utf-8"):



if __name__ == "__main__":
    try:
        test = ValidationParser(
            nb_drone=2,
            hub_peak=(
            "start_hub:",
            "hub",
            2,
            5,
            "[color=green]"
            ))
        print(test.model_dump())
    except Exception:
        print("error")
