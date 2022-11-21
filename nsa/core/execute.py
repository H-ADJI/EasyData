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
from nsa.core.utils import append_without_duplicate
from aiostream import stream
from nsa.constants.enums import ScrapingState

# move later to constants file
WORKFLOWS_LIST_INPUT_SEPARATOR = "|*|"


class PlanExecution:

    def __init__(self, plan: dict, browser: Browser = None, concurrent_workers_count: int = 3) -> None:
        self.plan: dict = plan
        self.browser: Browser = browser
        self.tab: BrowserTab = None
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

    async def compute_truth_value(self, page: Page, condition_type: Literal["no_more_elements", "max_element_count", "element_match_value"], elements_selector: str, attribute_name: str = None, value: str = None, count: int = None):
        elements: Locator = page.locator(selector=elements_selector)
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

    async def condition_handler(self, page: Page,  condition_data: dict = None):
        truth_value = True
        if conditions := condition_data.get("and"):
            truth_value = True
            for condition in conditions:
                truth_value = truth_value and await self.compute_truth_value(
                    page=page, **condition)
        elif conditions := condition_data.get("or"):
            truth_value = False
            for condition in conditions:
                truth_value = truth_value or await self.compute_truth_value(
                    page=page, **condition)
        elif conditions := condition_data.get("single"):
            truth_value = await self.compute_truth_value(page=page, **conditions)

        return truth_value

    def read_action(self, action_name: str):
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
        action = eval("self.tab." + action_name)
        return action

    async def do_once(self, page: Union[Page, None], interaction: dict, current_repition_data: dict = None, input_data: dict = None) -> dict:
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

        action: Callable = self.read_action(
            interaction_with_data.get("do_once"))
        action_inputs: dict = interaction_with_data.get("inputs", {})
        print(f"doing: ---------> { interaction_with_data.get('do_once')}")
        data: list = await action(**action_inputs)
        print(f"done : ---------> { interaction_with_data.get('do_once')}")

        if data:
            return data
        return []

    async def do_many(self, page, sub_interactions: dict, current_repition_data: dict = None, input_data: dict = None):
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
            repitition_data_output = []
            for interaction in interactions:
                # calling do_once to execute an action for every iteration of the current loop
                data = await self.do_once(page, interaction=interaction,
                                          current_repition_data={repitition["field"]: repitition["value"]}, input_data=input_data)

                if data:
                    for d in data:
                        d[repitition["field"]] = repitition["value"]
                    repitition_data_output.extend(data)
            yield repitition_data_output

    async def do_until(self, page, sub_interactions: dict, current_repition_data: dict = None, input_data: dict = None):
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
            repition_condition = await self.condition_handler(page=page, condition_data=conditions)
            output = []
            for interaction in interactions:
                data = await self.do_once(page, interaction=interaction,
                                          current_repition_data=current_repition_data, input_data=input_data)
                if data:
                    output.extend(data)
            yield output

    @staticmethod
    def input_data_batching(input_data: dict, field: str, chunk_size=3):
        data_list = input_data.get(field, [])

        data_chunks = [data_list[x:x+chunk_size]
                       for x in range(0, len(data_list), chunk_size)]
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
        concurrency_field: str = self.plan.get(
            "concurrency_field")
        interactions: list[dict] = self.plan.get("interactions")
        context = await self.browser.launch_context()
        queue = asyncio.Queue()
        if not concurrency_field:
            self.concurrent_workers_count = 1
            await queue.put(input_data)
        else:
            for input_chunk in self.input_data_batching(input_data, concurrency_field):
                await queue.put(input_chunk)
        # streaming (merging) all concurrent data generators into one to consume data from it
        # now the concurrency is done using multiple browser pages (tabs) we can use multiple context simply by not specifying the context when launching a page
        # TODO There is a more elegant way of distributing the scraping tasks on a limited number of workers ( either browser contexts or browser tabs ) using a semaphore or asyncio.wait
        # Sauce : https://stackoverflow.com/questions/48483348/how-to-limit-concurrency-with-python-asyncio
        workers = stream.merge(
            *[(self.worker(interactions=interactions, context=context, queue=queue)) for _ in range(min(queue.qsize(), self.concurrent_workers_count))])
        async with workers.stream() as streamer:
            async for data in streamer:
                yield data
        await self.browser.exit_context(context=context)

    async def worker(self, interactions: List[dict], context: BrowserContext, queue: asyncio.Queue):
        """_summary_

        Args:
            interactions (List[dict]): _description_
            context (BrowserContext): _description_
            queue (asyncio.Queue): _description_

        Yields:
            _type_: _description_
        """
        async with BrowserTab(context=context) as self.tab:

            while True:
                input_data = await queue.get()
                for interaction in interactions:
                    if interaction.get("do_once", None):
                        data = await self.do_once(page=self.tab.page, interaction=interaction, input_data=input_data)
                        if data:
                            yield data
                    elif interaction.get("do_many", None):
                        data_generator = self.do_many(
                            page=self.tab.page, sub_interactions=interaction, input_data=input_data)
                        if data_generator:
                            async for data in data_generator:
                                yield data
                    elif interaction.get("do_until", None):
                        data_generator = self.do_until(
                            page=self.tab.page, sub_interactions=interaction, input_data=input_data)
                        if data_generator:
                            async for data in data_generator:
                                yield data
                if queue.empty():
                    break


class GeneralPurposeScraper:
    # TODO add data persistence layer here ( data saving ...)
    def __init__(self) -> None:
        self.data_persistence = None
        self.website = None

    async def scrape(self, browser: Browser, plan: dict, input_data: dict = None) -> dict:
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
        plan_execution = PlanExecution(plan=plan, browser=browser)

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
                # TODO: place duplication removal into places when necessary so it doesn't have to be called every time we scrape
                scraped_data["scraped_data"] = append_without_duplicate(
                    data=data_batch, target=scraped_data["scraped_data"])
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
