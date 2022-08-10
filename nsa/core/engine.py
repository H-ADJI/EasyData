'''
File: browser.py
File Created: Monday, 18th July 2022 10:54:07 am
Author: KHALIL HADJI
-----
Copyright:  HENCEFORTH 2022
'''
from typing import List, Union
from abc import abstractmethod
import asyncio
from typing import Literal, Protocol
from playwright.async_api import BrowserContext, Page, Locator, Playwright
from nsa.core.preprocessing import data_processing
from nsa.errors.browser_errors import ActionsFallback, AttributeRetrievalError, WaitingError, ClickButtonError, UseKeyboardError
from playwright.async_api import TimeoutError as NavigationTimeout
from playwright.async_api import Browser as playwright_browser
import aiohttp
from bs4 import BeautifulSoup, ResultSet, Tag


class Engine(Protocol):
    # Protocols replace ABCs: where ABCs are run-time checks, Protocols provide static-checking, and can take place before run-time.

    @abstractmethod
    async def visit_url():
        raise NotImplementedError

    @abstractmethod
    async def scrape_page():
        raise NotImplementedError


class Browser(Engine):
    # TODO: Handle errors
    def __init__(self, configuration: dict = None) -> None:
        self.configuration = configuration

    async def launch_browser(playwright: Playwright, browser_configuration: dict, browser_type: Literal["chromium", "firefox", "webkit"]):
        browsers_choices = {"webkit": playwright.webkit,
                            "chromium": playwright.chromium, "firefox": playwright.firefox}
        browser = await browsers_choices.get(
            browser_type, playwright.chromium).launch()
        return browser

    async def launch_context(browser: playwright_browser, context_config: dict, default_scraping_timeout: float, default_navigation_timeout: float):
        context: BrowserContext = await browser.new_context(context_config)
        context.set_default_timeout(timeout=default_scraping_timeout)
        context.set_default_navigation_timeout(
            timeout=default_navigation_timeout)
        return context

    async def launch_page(context: BrowserContext, page_config=dict):
        page = await context.new_page(**page_config)
        return page

    @staticmethod
    async def handle_fallback(action, selectors: List[str] = None, **kwargs):
        """Function that will handle the retry-ability of a browser action based on a list of xpaths

        Args:
            - action : the browser action that will be retried
            - selectors (List[str]): list of xpaths or css selectors
        """
        if not selectors:
            selectors = ["*"]
        for i, selector in enumerate(selectors):
            print(
                "-------------------------------------------------------------------------")
            print(
                "RUNNING -->> {action}_action using XPATH N* --> {number}".format(action=action.__name__, number=i+1))
            try:
                action_result = await action(selector=selector, **kwargs)
                print(
                    "SUCCESS -->> {action}_action using XPATH N* --> {number}".format(action=action.__name__, number=i+1))
                print(
                    "-------------------------------------------------------------------------")
                return action_result
            except NavigationTimeout:
                print("FAILED -->> trying next selector...")
        raise(ActionsFallback(
            "Could not handle this interaction fallback with the provided selectors"))

    async def visit_page(page: Page, url: str = "https://www.google.com/", **kwargs):
        """navigate to a url

        Args:
            - url (str, optional): targeted url. Defaults to "https://www.google.com/".
            - tab_number (int, optional): choose which tab will be used in the navigation process. Defaults to 1.
        """
        if page.url == url:
            return
        await page.goto(url=url)

    async def click(element: Union[Page, Locator], selectors, count: int = 1, **kwargs):
        """Click the element(s) matching the selector(s)

        Args:
            - element (Union(Page,Locator)): a web browser element, could be either a tab (Page) or a Locator
            - selectors (List[str]): list of xpaths or css selectors
            - count (int, optional): number of click to execute. Defaults to 1.

        """
        click_action = element.click
        try:
            await Browser.handle_fallback(action=click_action, selectors=selectors, click_count=count, **kwargs)
        except ActionsFallback:
            raise(ClickButtonError(
                "Unable to click the provided selectors"))

    async def use_keyboard(element: Union[Page, Locator], keys: List[str],   selectors: List[str] = None, delay: float = 200, **kwargs):
        """Send keystrokes to the element(s) matching the selector(s)

        Args:
            - element (Union(Page,Locator)): a web browser element, could be either a tab (Page) or a Locator
            - selectors (List[str]): list of xpaths or css selectors
            #modifier_keys>'
            - keys (List[str]): keyboard keys to use  <https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/key/Key_Values
            - delay (float, optional): time delay between each button press and release. Defaults to 0.


        """
        type_action = element.press
        try:
            for key in keys:
                await Browser.handle_fallback(action=type_action, selectors=selectors, key=key, delay=delay, **kwargs)
        except ActionsFallback:
            raise(UseKeyboardError(
                "Unable to send keyboard keypress to element with the provided selectors"))

    async def wait_for(element: Union[Page, Locator], event: Literal["load", "domcontentloaded", "networkidle"] = None, selectors: List[str] = None, state: Literal["attached", "detached", "visible", "hidden"] = None, timeout: int = 10_000, **kwargs):
        if event:
            await element.wait_for_load_state(state=event, timeout=timeout)
        else:
            waiting_action = element.wait_for_selector
            try:
                await Browser.handle_fallback(action=waiting_action, selectors=selectors, state=state, timeout=timeout, **kwargs)
            except ActionsFallback:
                raise WaitingError

    async def relocate(element:  Locator, selectors: List[str] = None, iframe=None):
        if not selectors:
            return element
        for selector in selectors:
            if iframe:
                relocated_element = element.frame_locator(
                    iframe).locator(selector)
            else:
                relocated_element = element.locator(selector)
            element_count = await relocated_element.count()
            if element_count > 0:
                return relocated_element
        raise ActionsFallback

    async def scrape_page(element: Union[Page, Locator], data_to_get: List[dict], selectors: List[str] = None, include_order: bool = False, **kwargs):
        data_to_return = []
        try:
            elements = await Browser.relocate(selectors=selectors, element=element)
        except ActionsFallback:
            return data_to_return
        elements_count = await elements.count()
        for i in range(elements_count):
            current_element_data = {}
            current_element = elements.nth(i)
            if include_order:
                current_element_data["#"] = i + 1
            for d in data_to_get:

                current_element = elements.nth(i)
                if "relocate" in d:
                    try:
                        current_element = await Browser.relocate(selectors=d.get("relocate"), element=current_element, iframe=d.get("iframe"))
                    except ActionsFallback:
                        # if no element matched selector field will be None
                        print(f"field {d.get('field_alias')} not available")
                        current_element_data[d.get("field_alias")] = None
                        continue

                if d.get("kind") == "attribute":
                    data = await Browser.retrieve_attribute(element=current_element, data_to_get=d)

                elif d.get("kind") == "text":
                    data = await Browser.retrieve_text(element=current_element, data_to_get=d)

                elif d.get("kind") == "nested_field":
                    data = await Browser.retrieve_nested_field(element=current_element, data_to_get=d)

                elif d.get("kind") == "generated_field":
                    data = current_element_data[d.get("source_field")]

                processing = d.get("processing")
                if processing:
                    if data:
                        data = data_processing(
                            data=data, processing_pipline=processing)
                current_element_data[d.get("field_alias")] = data
            data_to_return.append(current_element_data)
        return data_to_return

    @staticmethod
    async def retrieve_attribute(element: Union[Page, Locator], data_to_get: dict):
        current_element_count = await element.count()
        attribute = []
        for j in range(current_element_count):
            current_sub_element = element.nth(j)
            data = await current_sub_element.get_attribute(name=data_to_get.get("name"))
            attribute.append(data)
        if data_to_get.get("find_all") == True:
            return attribute
        return attribute[0]

    @staticmethod
    async def retrieve_text(element: Union[Page, Locator], data_to_get: dict):
        current_element_count = await element.count()
        text = []
        for j in range(current_element_count):
            current_sub_element = element.nth(j)
            data = await current_sub_element.text_content()
            text.append(data)
        if data_to_get.get("find_all") == True:
            return text
        return text[0]

    @staticmethod
    async def retrieve_nested_field(element: Union[Page, Locator], data_to_get: dict):
        nested_field = await Browser.scrape_page(element=element, data_to_get=data_to_get.get("data_to_get"), **data_to_get.get("inputs", {}))
        if data_to_get.get("find_all") == True:
            return nested_field
        if not nested_field:
            return None
        return nested_field[0]


class HttpRequests(Engine):
    # TODO; this is the second engine for plain http request without js rendering, on stand by, will be developed until finishing the browser engine
    def __init__(self, configuration: dict = None) -> None:
        self.configuration = configuration or {}
        self.session = aiohttp.ClientSession(**self.configuration)
        self.content = None

    async def visit_page(self, url: str):
        async with self.session.get(url=url) as r:
            self.content = BeautifulSoup(markup=await r.text(), features="html.parser")

    def handle_fallback(action, selectors: List[str] = None, **kwargs):
        """Function that will handle the retry-ability of a browser action based on a list of xpaths

        Args:
            - action : the browser action that will be retried
            - selectors (List[str]): list of xpaths or css selectors
        """
        if not selectors:
            selectors = ["*"]
        for i, selector in enumerate(selectors):
            print(
                "-------------------------------------------------------------------------")
            print(
                "RUNNING -->> {action}_action using XPATH N* --> {number}".format(action=action.__name__, number=i+1))

            action_result = action(selector=selector, **kwargs)
            if action_result:
                print(
                    "SUCCESS -->> {action}_action using XPATH N* --> {number}".format(action=action.__name__, number=i+1))
                print(
                    "-------------------------------------------------------------------------")
                return action_result
            print("FAILED -->> trying next selector...")
        raise(ActionsFallback(
            "Could not handle this interaction fallback with the provided selectors"))

    def scrape_page(self, selectors: List[str], data_to_get: List[dict], include_order: bool = False, **kwargs):
        data_to_return = []
        try:
            elements: ResultSet[Tag] = self.content.select()
        except ActionsFallback:
            raise(AttributeRetrievalError(
                "Unable to locate the element(s) with provided selectors"))
        for i, current_element in enumerate(elements):
            current_element_data = {}
            if include_order:
                current_element_data["#"] = i + 1
            for d in data_to_get:
                element = current_element
                if "relocate" in d:
                    element = element.select_one(d.get("relocate"))
                if d.get("kind") == "attribute":
                    attribute = element.attrs[d.get["name"]]
                    current_element_data[d.get("field_alias")] = attribute
                elif d.get("kind") == "text":
                    text = element.text
                    current_element_data[d.get("field_alias")] = text
            data_to_return.append(current_element_data)
        return data_to_return
