# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  parsing.py                                        :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: samrazaf <samrazaf@student.42antananari   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/11/17 15:54:19 by samrazaf        #+#    #+#               #
#  Updated: 2026/11/18 17:24:13 by samrazaf        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from pydantic import BaseModel, Field
from typing import Annotated, Literal

class ParseError:
    def __init__(self, msg):
        pass

hub_type = Literal["start_hub:", "end_hub:"]

class ValidationParser_peak(BaseModel):
    hub_peak: tuple[
        hub_type,
        str,
        int,
        int,
        Annotated[str, Field(pattern=r"^\[color=[^.,\s]+\]$")]
    ]

class ValidationParser_hub(BaseModel):
    hub_peak: tuple[
        Annotated[str, Field(pattern=(r"^hub: $"))],
        str,
        int,
        int,
        Annotated[str, Field(pattern=(r"^\[zone=[^.,\s\d]+\scolor=[^.,\s\d]+( max_drones=\d+)?\]$"))]
    ]


#class Parsing:
#    def read_file(path):
#        with open(path, "r", encoding="utf-8"):



if __name__ == "__main__":
    try:
        test = ValidationParser_hub(
            hub_peak=(
            "hub: ",
            "roof",
            3,
            4,
            "[zone=normal color=green max_drones=5]"
            ))
        print(test.model_dump())
    except Exception:
        print("error")
