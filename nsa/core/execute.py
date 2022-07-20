'''
File: execute.py
File Created: Monday, 18th July 2022 10:54:07 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from typing import Callable, Generator, Iterable, Iterator
from collections import defaultdict
from nsa.core.browser import *


def read_plan_file(path: str, news_website: str):
    ...


def read_action(action: str):
    # TODO actions should be validated because eval is dangerous
    action = eval(action)
    return action


def inject_data_into_plan(raw_plan_dict: dict, data: dict):
    ...


def repitition_data_generator(interaction: dict):
    field = interaction.get("do_many")
    iter_over: Iterator = iter(interaction.get("list"))
    for it in iter_over:
        yield {"field": field, "value": it}


async def do_once(page: Page, interaction: dict, current_repition_data: dict = None):
    action: Callable = read_action(interaction.get("do_once"))
    selectors: list = interaction.get("selectors", [])
    input: dict = interaction.get("inputs", {})
    data = await action(page, **input)
    return data


async def do_many(sub_interactions: dict, number_iterations: int = 0):
    output = defaultdict(dict)
    repititions: Generator = repitition_data_generator(sub_interactions)
    interactions: list[dict] = sub_interactions.get("interactions")

    for repitition in repititions:
        print("--------------" + str(repitition) + "-------------- \n")
        output[repitition["field"]][repitition["value"]] = {}
        for interaction in interactions:
            if interaction.get("do_many", None):
                data = await do_many(sub_interactions=interaction)
                output[repitition["field"]][repitition["value"]
                                            ] = data
            else:
                data = await do_once(interaction=interaction,
                                     current_repition_data=repitition)
                output[repitition["field"]][repitition["value"]
                                            ] = data
    return dict(output)


async def execute_plam(page, plan: dict):
    # TODO: inject data to plan
    output = {}
    interactions: list[dict] = plan.get("interactions")
    for interaction in interactions:
        if interaction.get("do_once", None):
            data = await do_once(page, interaction=interaction)
            if data:
                output = output | dict(data)
            # print(output1)
        elif interaction.get("do_many", None):
            data = await do_many(page, sub_interactions=interaction)
            if data:
                output = output | dict(data)
    return output
