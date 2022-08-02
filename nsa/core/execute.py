'''
File: execute.py
File Created: Monday, 18th July 2022 10:54:07 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from time import time
from typing import Callable, Generator, Iterable, Iterator, Literal, Protocol
from collections import defaultdict
from nsa.core.engine import Browser, Engine, Page, Locator
import yaml
import json
import time
# move later to constants file
WORKFLOWS_LIST_INPUT_SEPARATOR = "|*|"


class WebsitePlan:
    PLANS_SCHEMA_FILE_PATH = ""
    PLANS_FILES_PATH = "./nsa/scraping_plan/"

    def __init__(self, website: str, plan_dict: dict = None) -> None:
        self.website: str = website
        self.plan_dict: dict = plan_dict

    def get_or_read_plan_file(self) -> dict:
        # TODO : turn into property for ease of use
        """Read scraping plan yaml file of a given news website

        Args:
            website (str): name of the website TODO: will be defined from an enum for exactitude

        Returns:
            dict: plan yaml file as a dict object
        """
        if not self.plan_dict:
            with open(self.PLANS_FILES_PATH + self.website + ".yml", "r") as yml:
                plan_dict: dict = yaml.load(yml, Loader=yaml.SafeLoader)
                self.plan_dict = WebsitePlan.validate_plan(plan=plan_dict)

        return self.plan_dict

    @staticmethod
    def validate_plan(plan: dict):
        # TODO: will be implemented to validate plans either using jsonschema or pydantic
        return plan


class PlanExecution:
    def __init__(self, plan: dict, engine: Engine = None) -> None:
        self.plan: dict = plan
        self.engine: Engine = engine
        self.previous_content_count: int = -1

    def inject_data_into_plan(raw_plan, data: dict = None):
        # TODO: Consider using OmegaConf / Hydra library for this task
        """this function allows data injection into plan dict objects

        Args:
            raw_plan_dict (dict): plan dict object 
            data (dict, optional): data to be injected . Defaults to None.

        Returns:
            dict: dict object with injected data 
        """
        raw_plan_str = json.dumps(raw_plan)
        if not data:
            formated_plan_str = raw_plan_str
        for parameter_name, parameter_value in data.items():
            parameter_name = "{"+parameter_name+"}"
            if isinstance(parameter_value, list):
                parameter_value_str = [*map(str, parameter_value)]
                formated_plan_str: str = raw_plan_str.replace(
                    parameter_name, WORKFLOWS_LIST_INPUT_SEPARATOR.join(parameter_value_str))
            else:
                formated_plan_str: str = raw_plan_str.replace(
                    parameter_name, str(parameter_value))
            raw_plan_str = formated_plan_str

        formated_plan: dict = json.loads(formated_plan_str)
        return formated_plan

    @staticmethod
    def repitition_data_generator(interaction: dict):
        """Handles looping mechanism to do actions over a list of elements 
            TODO: Handle other types of loops, like looping for fixed amount of repetition (aka for i in range)
            or looping until a condition is met ( aka while condition )

        Args:
            interaction (dict): the interaction that will be repeated

        Yields:
            dict: fields that will be used for each interaction iteration 
        """
        field = interaction.get("do_many")

        # this is the case where we inject a list into a yaml file and that we want to interate over each element of the list
        iteractions_list = interaction.get("for_each")
        print(interaction)
        if iteractions_list:
            # the list is injected as a string so we should parse it into an actual python list object using "List.split('separator')"
            if isinstance(iteractions_list, str):
                iteractions_list = iteractions_list.split(
                    WORKFLOWS_LIST_INPUT_SEPARATOR)

            # this is the case where we handle a loop over a python list
            if isinstance(iteractions_list, list):
                iter_over: Iterator = iter(iteractions_list)

        # this is the case where we handle a loop over a range
        iteractions_range = interaction.get("for")
        if iteractions_range:
            iter_over = range(iteractions_range)

        for it in iter_over:
            yield {"field": field, "value": it}

    async def condition_handler(self, page: Page, condition_type: Literal["count", "match_value", "no_more"], elements_selector: str, value: str | int = None):
        elements: Locator = page.locator(selector=elements_selector)
        if condition_type == "match_value":
            content_count = await elements.count()
            for i in range(content_count):
                content = await elements.nth(i).text_content()
                if content == value:
                    return True
        elif condition_type == "count":
            content_count = await elements.count()
            print(content_count)
            if content_count >= value:
                return True
        elif condition_type == "no_more":
            if self.previous_content_count == await elements.count():
                return True
            self.previous_content_count = await elements.count()
        return False

    @staticmethod
    def read_action(action_name: str):
        """Read actions from yaml file and transform them into callables, to do this there is three aproaches  :

        -- either using eval function or a switch/case over all available function, eval is dangerous and we should restrict it for safety Exp : eval(os.system(' rm -rf * ')) will destroy everything.

        -- switch/case require a lot of code lines and manual intervention if any other function is added.

        -- Or we can retrieve the action from a dictionary object that maps action_names to their callables ( safest and cleanest approach ).

        Args:
            action_name (str): action name

        Returns:
            Callable: action callable function
        """
        # TODO actions should be validated because eval is dangerous
        action = eval("Browser." + action_name)
        return action

    async def do_once(self, page: Page, interaction: dict, current_repition_data: dict = None, user_data: dict = None) -> dict:
        """Handle a single action execution and return its data results if there is any

        Args:
            page (Page): page on which to launch the action 
            interaction (dict): interaction that we will be executing
            current_repition_data (dict, optional): data that is needed if this function call was nested in a loop. Defaults to None.
            user_data (dict, optional): any data provided by the user that will be needed for the action. Defaults to None.

        Returns:
            dict: feedback data from the websites
        """

        # this is the data that will be injected into the scraping plan
        # current_repition_data : this is passed if the current action is in the context of a loop
        current_repition_data = current_repition_data or {}
        # user_data : this is data provided by a user and that should be used when executing the scraping plan
        user_data = user_data or {}

        interaction_with_data: dict = PlanExecution.inject_data_into_plan(
            raw_plan=interaction, data=current_repition_data | user_data)

        action: Callable = PlanExecution.read_action(
            interaction_with_data.get("do_once"))
        action_inputs: dict = interaction_with_data.get("inputs", {})

        data: list = await action(page, **action_inputs)
        return {'hits': data}

    async def do_many(self, page, sub_interactions: dict, current_repition_data: dict = None, user_data: dict = None):
        """Handle case where we have a loop of action over a list, a range or until a condition
        recursively calls itself if there is nested loops 

        Args:
            page (Page): page on which to launch the action
            sub_interactions (dict): interaction that we will be looping over and executing
            current_repition_data (dict, optional): data that is needed if this function call was nested in a loop. Defaults to None.
            user_data (dict, optional): any data provided by the user that will be needed for the action. Defaults to None.

        Returns:
            dict: feedback data from the websites
        """
        # this is the data that will be injected into the scraping plan
        # current_repition_data : this is passed if the current action is in the context of a loop
        current_repition_data = current_repition_data or {}
        # user_data : this is data provided by a user and that should be used when executing the scraping plan
        user_data = user_data or {}

        interaction_with_data: dict = PlanExecution.inject_data_into_plan(
            raw_plan=sub_interactions, data=current_repition_data | user_data)

        # output will contains the nested output of all the do_once and do_many recursive calls
        output = defaultdict(dict)
        # data that will be used for every loop iteration
        repititions: Generator = PlanExecution.repitition_data_generator(
            interaction_with_data)
        interactions: list[dict] = interaction_with_data.get("interactions")
        for repitition in repititions:

            output[repitition["field"]][repitition["value"]] = {}
            for interaction in interactions:
                if interaction.get("do_many", None):
                    # recursively calling do_many for nested loops.
                    # when calling do_many or do_once we provide the current repitition data and the user data
                    data = await self.do_many(page, sub_interactions=interaction, current_repition_data={repitition["field"]: repitition["value"]}, user_data=user_data)
                    if data:
                        output[repitition["field"]][repitition["value"]
                                                    ] = data

                else:
                    # calling do_once to execute an action for every iteration of the current loop
                    data = await self.do_once(page, interaction=interaction,
                                              current_repition_data={repitition["field"]: repitition["value"]}, user_data=user_data)
                    if data:
                        output[repitition["field"]][repitition["value"]
                                                    ] = data

        return dict(output)

    async def do_until(self, page, sub_interactions: dict, current_repition_data: dict = None, user_data: dict = None):
        # this is the data that will be injected into the scraping plan
        # current_repition_data : this is passed if the current action is in the context of a loop
        current_repition_data = current_repition_data or {}
        # user_data : this is data provided by a user and that should be used when executing the scraping plan
        user_data = user_data or {}
        interaction_with_data: dict = PlanExecution.inject_data_into_plan(
            raw_plan=sub_interactions, data=current_repition_data | user_data)
        condition_type = interaction_with_data.get("do_until")
        condition_data = interaction_with_data.get("condition")
        interactions: list[dict] = interaction_with_data.get("interactions")
        condition = await self.condition_handler(page=page, condition_type=condition_type, **condition_data)
        output = {}
        while not condition:
            for interaction in interactions:
                if interaction.get("do_many", None):
                    data = await self.do_many(page, sub_interactions=interaction, current_repition_data=current_repition_data, user_data=user_data)
                if interaction.get("do_once", None):
                    data = await self.do_once(page, interaction=interaction,
                                              current_repition_data=current_repition_data, user_data=user_data)
                output = output | data
            condition = await self.condition_handler(page=page, condition_type=condition_type, **condition_data)

        return output

    async def execute_plam(self, page, objective: str, user_data: dict = None):
        """launch the execution of a scraping plan and returns the scraped data

        Args:
            page (_type_): browser page
            plan (dict): scraping plan describing steps to scrape a website
            user_data (dict, optional): data provided by the user that will be useful during the scraping. Defaults to None.

        Returns:
            dict: data scraped
        """
        output = {}
        plan: dict = self.plan.get(objective)
        interactions: list[dict] = plan.get("interactions")
        for interaction in interactions:
            if interaction.get("do_once", None):
                data = await self.do_once(page, interaction=interaction, user_data=user_data)
                if data:
                    print(data)
                    output = output | dict(data)
            elif interaction.get("do_many", None):
                data = await self.do_many(page, sub_interactions=interaction, user_data=user_data)
                if data:
                    print(data)
                    output = output | dict(data)
            elif interaction.get("do_until", None):
                data = await self.do_until(page, sub_interactions=interaction, user_data=user_data)
                if data:
                    print(data)
                    output = output | dict(data)
        return data


class GeneralPurposeScraper:
    # TODO add data persistence layer here with support of concurrency
    async def scrape(using: Engine, website: str, objective: str, user_data: dict = None) -> dict:
        """scrape a website according to specific defined objectives

        Args:
            using : the engine to use for the scraping
            website (str): name of the website to scrape
            objectives (str | list[str]): objective describing what data we will get 
            user_data (dict, optional): data that will be used to alter the scraping process. Defaults to None.

        Returns:
            dict: scraped data
        """
        scraped_data = {}
        website_plan: WebsitePlan = WebsitePlan(website=website)
        plan_execution = PlanExecution(
            plan=website_plan.get_or_read_plan_file())
        scraped_data[objective] = await plan_execution.execute_plam(page=using, objective=objective, user_data=user_data)
        return scraped_data
