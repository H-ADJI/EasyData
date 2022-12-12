'''
File: execute.py
File Created: Monday, 18th July 2022 10:54:07 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from datetime import datetime
import asyncio
from time import time
from typing import Any, Callable, Generator,  Iterator,  Literal,  Union, List
from nsa.core.engine import Browser,  Page, Locator, BrowserTab, BrowserContext
from nsa.errors.browser_errors import BrowserException
import json
from aiostream import stream
from nsa.constants.enums import ScrapingState
from nsa.core.processing import Data_Processing
# move later to constants file
WORKFLOWS_LIST_INPUT_SEPARATOR = "|*|"


class PlanExecution:
    browser_actions = {
        "navigate": BrowserTab.navigate,
        "scrape_page": BrowserTab.scrape_page,
        "scroll_down": BrowserTab.scroll_down,
        "use_keyboard": BrowserTab.use_keyboard,
        "click": BrowserTab.click,
        "block_routes": BrowserTab.block_routes,
        "wait_for": BrowserTab.wait_for,
        "wait_for_dom_mutation": BrowserTab.wait_for_dom_mutation,
        "pause": BrowserTab.pause,
    }

    def __init__(self, plan: dict, browser: Browser = None, concurrent_workers_count: int = 10) -> None:
        self.plan: dict = plan
        self.browser: Browser = browser
        # how many pages to use for the scraping
        self.concurrent_workers_count = concurrent_workers_count
        # be careful when running multiple scraping plan concurrently that may modify the same value
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

        Args:
            interaction (dict): the interaction that will be repeated

        Yields:
            dict: fields that will be used for each interaction iteration 
        """
        field = interaction.get("do_many")

        # this is the case where we inject a list into a yaml file and that we want to interate over each element of the list
        iteractions_list = interaction.get("for_each")
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

    async def compute_truth_value(self, browser_tab: BrowserTab, condition_type: Literal["no_more_elements", "max_element_count", "element_match_value"], elements_selector: str, attribute_name: str = None, value: str = None, count: int = None):
        elements: Locator = browser_tab.page.locator(
            selector=elements_selector)
        content_count = await elements.count()
        if condition_type == "element_match_value":
            for i in range(content_count):
                if not attribute_name:
                    content = await elements.nth(i).text_content()
                else:
                    content = await elements.nth(i).get_attribute(name=attribute_name)
                if content == value:
                    return True

        elif condition_type == "max_element_count":
            if content_count >= count:
                return True

        elif condition_type == "no_more_elements":
            if self.previous_content_count == content_count:
                return True
            self.previous_content_count = await elements.count()

        return False

    async def condition_handler(self, browser_tab: BrowserTab, condition_data: dict = None):
        truth_value = True
        if conditions := condition_data.get("and"):
            truth_value = True
            for condition in conditions:
                truth_value = truth_value and await self.compute_truth_value(
                    browser_tab=browser_tab, **condition)
        elif conditions := condition_data.get("or"):
            truth_value = False
            for condition in conditions:
                truth_value = truth_value or await self.compute_truth_value(
                    browser_tab=browser_tab, **condition)
        elif conditions := condition_data.get("single"):
            truth_value = await self.compute_truth_value(browser_tab=browser_tab, **conditions)

        return truth_value

    async def do_once(self, browser_tab: Union[Page, None], interaction: dict, current_repition_data: dict = None, input_data: dict = None) -> dict:
        """
        Handle a single action execution and return its data results if there is any

        Args:
            page (Page): page on which to launch the action 
            interaction (dict): interaction that we will be executing
            current_repition_data (dict, optional): data that is needed if this function call was nested in a loop. Defaults to None.
            input_data (dict, optional): any data provided by the user that will be needed for the action. Defaults to None.

        Returns:
            dict: feedback data from the websites
        """
        # this is the data that will be injected into the scraping plan
        # current_repition_data : this is passed if the current action is in the context of a loop
        current_repition_data = current_repition_data or {}
        # input_data : this is data provided by a user and that should be used when executing the scraping plan
        input_data = input_data or {}

        interaction_with_data: dict = PlanExecution.inject_data_into_plan(
            raw_plan=interaction, data={**current_repition_data, **input_data})

        action_name = interaction_with_data.get("do_once")
        action_callable: Callable = PlanExecution.browser_actions.get(
            action_name)
        action_inputs: dict = interaction_with_data.get("inputs", {})
        start_time = time()
        data: list = await action_callable(self=browser_tab, **action_inputs)
        print(
            f"done : ---------> { interaction_with_data.get('do_once')} ---- Took : {time()-start_time:4.2}s")

        if data:
            return data
        return []

    async def do_many(self, browser_tab: BrowserTab, sub_interactions: dict, current_repition_data: dict = None, input_data: dict = None):
        """
        Handle case where we have a loop of action over a list, a range or until a condition
        recursively calls itself if there is nested loops 

        Args:
            page (Page): page on which to launch the action
            sub_interactions (dict): interaction that we will be looping over and executing
            current_repition_data (dict, optional): data that is needed if this function call was nested in a loop. Defaults to None.
            input_data (dict, optional): any data provided by the user that will be needed for the action. Defaults to None.

        Returns:
            dict: feedback data from the websites
        """
        # this is the data that will be injected into the scraping plan
        # current_repition_data : this is passed if the current action is in the context of a loop
        current_repition_data = current_repition_data or {}
        # input_data : this is data provided by a user and that should be used when executing the scraping plan
        input_data = input_data or {}

        interaction_with_data: dict = PlanExecution.inject_data_into_plan(
            raw_plan=sub_interactions, data={**current_repition_data, **input_data})

        # output will contains the nested output of all the do_once and do_many recursive calls
        # data that will be used for every loop iteration
        repititions: Generator = PlanExecution.repitition_data_generator(
            interaction_with_data)
        interactions: list[dict] = interaction_with_data.get("interactions")
        for repitition in repititions:
            repitition_data_output_dict = {}
            repitition_data_output_list = []
            for interaction in interactions:
                # calling do_once to execute an action for every iteration of the current loop
                data = await self.do_once(browser_tab, interaction=interaction,
                                          current_repition_data={repitition["field"]: repitition["value"]}, input_data=input_data)

                if data:
                    data[repitition["field"]] = repitition["value"]
                    if isinstance(data, list):
                        repitition_data_output_list.extend(data)
                    if isinstance(data, dict):
                        repitition_data_output_dict.update(data)
            yield repitition_data_output_list or repitition_data_output_dict

    async def do_until(self, browser_tab: BrowserTab, sub_interactions: dict, current_repition_data: dict = None, input_data: dict = None):
        """repeat the execution of a set of interactions until a condition

        Args:
            page (Page): Page on which we evaluate the condition
            sub_interactions (dict): interaction that will be repeated
            current_repition_data (dict, optional): data that is needed if this function call was nested in a loop. Defaults to None.
            input_data (dict, optional): any data provided by the user that will be needed for the action. Defaults to None.

        Yields:
            _type_: _description_
        """
        # this is the data that will be injected into the scraping plan
        # current_repition_data : this is passed if the current action is in the context of a loop
        current_repition_data = current_repition_data or {}
        # input_data : this is data provided by a user and that should be used when executing the scraping plan
        input_data = input_data or {}
        interaction_with_data: dict = PlanExecution.inject_data_into_plan(
            raw_plan=sub_interactions, data={**current_repition_data, **input_data})
        conditions = interaction_with_data.get("do_until")
        interactions: list[dict] = interaction_with_data.get("interactions")
        repition_condition = False
        while not repition_condition:
            repition_condition = await self.condition_handler(browser_tab=browser_tab, condition_data=conditions)
            output = []
            for interaction in interactions:
                data = await self.do_once(browser_tab, interaction=interaction,
                                          current_repition_data=current_repition_data, input_data=input_data)
                if data:
                    if isinstance(data, list):
                        output.extend(data)
                    else:
                        output.append(data)
            yield output

    def input_data_batching(self, input_data: dict, field: str):
        data_list = input_data.get(field, [])
        data_size = len(data_list)
        chunk_size = max(data_size//self.concurrent_workers_count, 1)
        print([*range(1, data_size, chunk_size)])
        data_chunks = [data_list[x:x+chunk_size]
                       for x in range(data_size % self.concurrent_workers_count, data_size, chunk_size)]
        for chunk in data_chunks:
            yield {**input_data, **{field: chunk}}

    async def execute_plam(self, input_data: dict = None):
        """launch the execution of a scraping plan and returns the scraped data

        Args:
            input_data (dict, optional): data provided by the user that will be useful during the scraping. Defaults to None.
            objective (dict, optional): data provided by the user that will be useful during the scraping. Defaults to None.

        Returns:
            dict: data scraped
        """
        data_generator = range(1)
        if concurrency_field := self.plan.get(
                "concurrency_field"):
            data_generator = self.input_data_batching(
                input_data, concurrency_field)
        interactions: list[dict] = self.plan.get("interactions")
        context = await self.browser.launch_context()
        data_stream = stream.merge(
            *[(self.worker(interactions=interactions, context=context, input_data=data)) for data in data_generator])
        # streaming (merging) all concurrent data generators into one to consume data from it
        # now the concurrency is done using multiple browser pages (tabs) we can use multiple context simply by not specifying the context when launching a page
        async with data_stream.stream() as streamer:
            async for data in streamer:
                yield data
        await self.browser.exit_context(context=context)

    async def worker(self, interactions: List[dict], context: BrowserContext, input_data: dict):
        async with BrowserTab(browser=self.browser, context=context) as tab:
            for interaction in interactions:
                if interaction.get("do_once", None):
                    data = await self.do_once(browser_tab=tab, interaction=interaction, input_data=input_data)
                    if data:
                        yield data
                elif interaction.get("do_many", None):
                    data_generator = self.do_many(
                        browser_tab=tab, sub_interactions=interaction, input_data=input_data)
                    if data_generator:
                        async for data in data_generator:
                            yield data
                elif interaction.get("do_until", None):
                    data_generator = self.do_until(
                        browser_tab=tab, sub_interactions=interaction, input_data=input_data)
                    if data_generator:
                        async for data in data_generator:
                            yield data


class GeneralPurposeScraper:
    def __init__(self, browser: Browser) -> None:
        self.browser = browser

    async def scrape(self, plan: dict, input_data: dict = None) -> dict:
        """scrape a website according to specific defined objectives

        Args:
            browser : the playwright browser instance to use for the scraping
            website (str): name of the website to scrape
            objectives (str) : objective describing what data we will get 
            input_data (dict, optional): data that will be used to alter the scraping process. Defaults to None.

        Returns:
            dict: scraped data
        """
        scraped_data = {}
        plan_execution = PlanExecution(plan=plan, browser=self.browser)
        processing = Data_Processing(processing_pipline=plan.get("processing"))
        data_generator = plan_execution.execute_plam(input_data=input_data)
        i = 0
        # --metadata about scraping process--
        scraped_data["scraped_data"] = []
        scraped_data["date_of_scraping"] = None
        scraped_data["total"] = 0
        scraped_data["state"] = "Unstarted"
        scraped_data["took"] = 0
        start = time()
        state = ScrapingState.NOT_STARTED
        try:
            async for data_batch in data_generator:
                print(f"data_batch N\"{i+1}")
                i += 1
                if isinstance(data_batch, list):
                    scraped_data["scraped_data"].extend(data_batch)
                elif isinstance(data_batch, dict):
                    scraped_data["scraped_data"].extend([data_batch])

            # after the scraping phase the proceszsing functions are applied on the data we gathered
            # TODO: error handling and logging for processing
            scraped_data["scraped_data"] = processing.data_processing(
                data=scraped_data["scraped_data"])
            state = ScrapingState.FINISHED
        except BrowserException as e:
            error_repr = e.__class__.__name__ + " ---> " + e.__str__()
            print(error_repr)
            state = ScrapingState.ABORTED
        except Exception as e:
            error_repr = e.__class__.__name__ + " ---> " + e.__str__()
            print(error_repr)
        finally:
            scraped_data["date_of_scraping"] = datetime.now(
            ).isoformat(timespec="minutes")
            scraped_data["total"] = len(
                scraped_data["scraped_data"])
            scraped_data["state"] = state
            scraped_data["took"] = time() - start
            if state == ScrapingState.ABORTED:
                scraped_data["error_trace"] = error_repr
            return scraped_data
