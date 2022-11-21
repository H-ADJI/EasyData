'''
File: browser.py
File Created: Monday, 18th July 2022 10:54:07 am
Author: KHALIL HADJI
-----
Copyright:  HENCEFORTH 2022
'''
import random
import re
from typing import List, Literal, Union

from playwright.async_api import BrowserContext, Locator, Page
from playwright.async_api import TimeoutError as NavigationTimeout
from playwright.async_api import async_playwright

from nsa.core.mutation_observer import MutationObserver
from nsa.core.processing import Data_Processing
from nsa.errors.browser_errors import (ActionsFallback,
                                       AttributeRetrievalError,
                                       ClickButtonError,
                                       TextRetrievalError,
                                       UseKeyboardError, WaitingError)
from nsa.services.aio_object import AioObject


class BrowserTab:
    def __init__(self, context: BrowserContext = None) -> None:
        self.context = context
        self.page: Page = None
        self.mutation_observer = None
        self.data_processing = Data_Processing()
        self._id = None

    async def __aenter__(self):
        if self.page:
            print(f"page {self._id} already open")
            return self.page
        elif self.context:
            self.page = await self.context.new_page()
        self._id = random.randint(1, 1000)
        print(f"LAUNCHING A PAGE ---- id ->> {self._id}")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        print(f"CLOSING PAGE ---- id ->> {self._id}")
        await self.page.close()

    async def pause(self):
        await self.page.pause()

    async def navigate(self, url: str = "https://www.google.com/"):
        """navigate to a url

        Args:
            - url (str, optional): targeted url. Defaults to "https://www.google.com/".
            - tab_number (int, optional): choose which tab will be used in the navigation process. Defaults to 1.
        """
        if self.page.url == url:
            return
        await self.page.goto(url=url)

    async def block_routes(self, url_patterns: List[str]):
        for pattern in url_patterns:
            await self.page.route(re.compile(pattern),
                                  lambda route: route.abort())
            break

    async def click(self, selectors, count: int = 1, **kwargs):
        """Click the element(s) matching the selector(s)

        Args:
            - element (Union(Page,Locator)): a web browser element, could be either a tab (Page) or a Locator
            - selectors (List[str]): list of xpaths or css selectors
            - count (int, optional): number of click to execute. Defaults to 1.

        """
        click_action = self.page.click
        try:
            await Browser.handle_fallback(action=click_action, selectors=selectors, click_count=count, **kwargs)
        except ActionsFallback:
            raise (ClickButtonError(
                "Unable to click the provided selectors"))

    async def use_keyboard(self, keys: List[str],   selectors: List[str] = None, delay: float = 200, **kwargs):
        """Send keystrokes to the element(s) matching the selector(s)

        Args:
            - element (Union(Page,Locator)): a web browser element, could be either a tab (Page) or a Locator
            - selectors (List[str]): list of xpaths or css selectors
            #modifier_keys>'
            - keys (List[str]): keyboard keys to use  <https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/key/Key_Values
            - delay (float, optional): time delay between each button press and release. Defaults to 0.


        """
        type_action = self.page.press
        try:
            for key in keys:
                await Browser.handle_fallback(action=type_action, selectors=selectors, key=key, delay=delay, **kwargs)
        except ActionsFallback:
            raise (UseKeyboardError(
                "Unable to send keyboard keypress to element with the provided selectors"))

    async def wait_for(self, event: Literal["load", "domcontentloaded", "networkidle"] = None, selectors: List[str] = None, duration: int = 0, state: Literal["attached", "detached", "visible", "hidden"] = None, timeout: int = 10_000, **kwargs) -> None:
        """wait until a change (events or elements changes) happens on a page or an locator element then returns

        Args:
            element (Union[Page, Locator]): The element that we will be watching for changes.
            event (Literal[&quot;load&quot;, &quot;domcontentloaded&quot;, &quot;networkidle&quot;], optional): event to watch for before returning . Defaults to None.
            selectors (List[str], optional): used to watch for a sub element instead. Defaults to None.
            state (Literal[&quot;attached&quot;, &quot;detached&quot;, &quot;visible&quot;, &quot;hidden&quot;], optional): the state of the element to wait for before returning. Defaults to None.
            timeout (int, optional): time to wait watching for the changes to happens (bare in mind that the maximum possible duration before raising the waiting Exeption is len(selectors)*timeout). Defaults to 10_000.

        Raises:
            WaitingError: _description_
        """
        if event:
            try:
                await self.page.wait_for_load_state(state=event, timeout=timeout)
            except:
                raise WaitingError(
                    f"Waiting for {event} exceded timeout --> {timeout} ms <-- ")

        elif duration:
            await self.page.wait_for_timeout(duration*1000)
        else:
            waiting_action = self.page.wait_for_selector
            try:
                await Browser.handle_fallback(action=waiting_action, selectors=selectors, state=state, timeout=timeout, **kwargs)
            except ActionsFallback:
                raise WaitingError(
                    f"Waiting for {selectors.__str__()} to be {state} exceded timeout {timeout} ms ")

    async def wait_for_dom_mutation(self, selectors: List[str], **kwargs):
        if not self.mutation_observer:
            target_element = await self.relocate(element=self.page, selectors=selectors)
            self.mutation_observer: MutationObserver = await MutationObserver(
                target_element=target_element)
        await self.mutation_observer.resolve(**kwargs)

    async def relocate(self, element:  Union[Page, Locator] = None, selectors: List[str] = None, iframe=None) -> Union[Page, Locator]:
        """this method match a sub-element from the 'element' input using the selectors list 

        Args:
            element (Union[Page, Locator]): the element in which we will be searching for sub-elements 
            selectors (List[str], optional): a list of selectors to handle the retry-ability. Defaults to None.
            iframe (_type_, optional): used in case you want to relocate into an iframe element. Defaults to None.

        Raises:
            ActionsFallback: in case to element was matched the exceptio nis raised

        Returns:
            Union[Page, Locator]: the matched sub-element(s)
        """
        if not element:
            element = self.page
        if not selectors:
            return element

        if iframe:
            for selector in selectors:
                relocated_element = element.frame_locator(
                    iframe).locator(selector)
                try:
                    element_count = await relocated_element.count()
                except Exception as e:
                    print(
                        f"relocating into the iframe caused the following exeption {e.__str__()} ")
                    raise ActionsFallback(
                        f"relocating into the iframe caused the following exeption {e.__str__()} ")
                if element_count > 0:
                    return relocated_element

            raise ActionsFallback

        else:
            for selector in selectors:
                relocated_element = element.locator(selector)
                element_count = await relocated_element.count()
                if element_count > 0:
                    return relocated_element
        raise ActionsFallback

    async def scrape_page(self, data_to_get: List[dict], element: Union[Page, Locator] = None, selectors: List[str] = None, include_order: bool = False, **kwargs):
        data_to_return = []
        try:
            # relocate to select elements within the current page / element using the selectors
            elements = await self.relocate(selectors=selectors, element=element)
        except ActionsFallback:
            return data_to_return
        # counting elements matched after relocating
        elements_count = await elements.count()
        for i in range(elements_count):
            # object that will contain data for each element matched
            current_element_data = {}
            current_element = elements.nth(i)

            # if the order of the scraped elements is to be included in the ouput data
            if include_order:
                current_element_data["ranking"] = i + 1

            # reading data fields to extract from the current element
            for d in data_to_get:
                current_element = elements.nth(i)
                if "relocate" in d:
                    try:
                        # relocate to a sub-element if required ( could be an iframe )
                        current_element = await self.relocate(selectors=d.get("relocate"), element=current_element, iframe=d.get("iframe"))
                    except ActionsFallback:
                        # if no element matched, field will be set to None
                        print(f"field {d.get('field_alias')} not available")
                        current_element_data[d.get("field_alias")] = None
                        # moving into the next data field to be extracted
                        continue
                # 4 type of fields can be extracted
                # attribute contained in an html element
                if d.get("kind") == "attribute":
                    data = await self.retrieve_attribute(element=current_element, data_to_get=d)
                # text from an html element
                elif d.get("kind") == "text":
                    data = await self.retrieve_text(element=current_element, data_to_get=d)
                # nested field that contain other fields (attributes and text)
                elif d.get("kind") == "nested_field":
                    data = await self.retrieve_nested_field(element=current_element, data_to_get=d)
                    # if a nested object field are all None we change the value to a single None
                    data = self.data_processing.empty_data_to_None(data)
                # a generated field is one that is created using aggregation on another field
                elif d.get("kind") == "generated_field":
                    data = current_element_data[d.get("source_field")]
                # processing to be done on the created fields above
                processing = d.get("processing")
                if processing:
                    if data:
                        data = self.data_processing.data_processing(
                            data=data, processing_pipline=processing)

                # inserting the field in a dictionary object
                current_element_data[d.get("field_alias")] = data
            data_to_return.append(current_element_data)
        return data_to_return

    @staticmethod
    async def retrieve_attribute(element: Union[Page, Locator], data_to_get: dict) -> Union[list, str, None]:
        """extracting an attribute from a page elements

        Args:
            element (Union[Page, Locator]): element from whom the data is scraped
            data_to_get (dict): a description of the detail and specificities of the data to scrape

        Returns:
            Union[list, str, None]: the extracted attribute(s)
        """
        try:
            # the count of the elements that matched
            current_element_count = await element.count()
            attribute = []
            for j in range(current_element_count):
                current_sub_element = element.nth(j)
                # Handling different attributes names in case of different selectors
                for name in data_to_get.get("name"):
                    data = await current_sub_element.get_attribute(name=name)
                    if data:
                        break
                # inserting all scraped attributes
                attribute.append(data)

            # controls if we trying to scrape a single element or multiple ones
            if data_to_get.get("find_all") == True:
                return attribute
            return attribute[0]
        except:
            raise AttributeRetrievalError(
                f"Could not extract {data_to_get.get('field_alias')}")

    @staticmethod
    async def retrieve_text(element: Union[Page, Locator], data_to_get: dict) -> Union[list, str, None]:
        """extracting text from a page elements

        Args:
            element (Union[Page, Locator]): element from whom the data is scraped
            data_to_get (dict): a description of the detail and specificities of the data to scrape

        Returns:
            Union[list, str, None]: the extracted text(s)
        """
        try:
            # the count of the elements that matched
            current_element_count = await element.count()
            text = []
            for j in range(current_element_count):
                current_sub_element = element.nth(j)
                data = await current_sub_element.text_content()
                text.append(data)

            # controls if we trying to scrape a single element or multiple ones
            if data_to_get.get("find_all") == True:
                return text
            return text[0]
        except:
            raise TextRetrievalError(
                f"Could not extract {data_to_get.get('field_alias')}")

    async def retrieve_nested_field(self, element: Union[Page, Locator], data_to_get: dict) -> Union[list, dict, None]:
        """recursively calls Browser.scrape page to create data in nested dictionary objects

        Args:
            element (Union[Page, Locator]): element from whom the data is scraped
            data_to_get (dict): a description of the detail and specificities of the data to scrape

        Returns:
            Union[list, dict, None]: the extracted data
        """

        # recursively calling Browser.scrape_page to create a nested field that may contain other fields : text, attributes and other nested fields
        nested_field = await self.scrape_page(element=element, data_to_get=data_to_get.get("data_to_get"), **data_to_get.get("inputs", {}))

        # controls if we trying to scrape a single element or multiple ones
        if data_to_get.get("find_all") == True:
            return nested_field

        # if the nested field is an empty dict
        if not nested_field:
            return None
        return nested_field[0]


class Browser(AioObject):
    """_summary_

    """
    async def __init__(self, engine_type: Literal["webkit", "firefox", "chromium"] = "chromium", navigation_timeout: float = 30_000, scraping_timeout: float = 30_000, browser_configuration: dict = None, context_configuration: dict = None, page_configuration: dict = None, browser_type: Literal["chromium", "firefox", "webkit"] = "chromium") -> None:
        print(
            "************************ ---launching the browser--- ************************")
        self.browser_configuration = browser_configuration
        self.context_configuration = context_configuration
        self.page_configuration = page_configuration
        self.navigation_timeout = navigation_timeout
        self.scraping_timeout = scraping_timeout
        self.engine_type = engine_type
        self.playwright_engine = await async_playwright().start()
        browsers_choices = {"webkit": self.playwright_engine.webkit,
                            "chromium": self.playwright_engine.chromium, "firefox": self.playwright_engine.firefox}
        self.browser = await browsers_choices.get(
            engine_type, self.playwright_engine.chromium).launch(headless=True)
        self.browser_context = None
        print("************************ ---succesfully launched the browser--- ************************")

    async def exit_browser(self):
        print(
            "************************ ---Exiting the browser--- ************************")
        await self.browser.close()
        await self.playwright_engine.stop()
        print(
            "************************ ---succesfully stopped the browser--- ************************")

    async def launch_context(self):
        print(
            "************************ ---launching the browser context--- ************************")
        self.browser_context: BrowserContext = await self.browser.new_context()
        self.browser_context.set_default_timeout(timeout=self.scraping_timeout)
        self.browser_context.set_default_navigation_timeout(
            timeout=self.navigation_timeout)
        print("************************ ---succesfully launched the browser context--- ************************")
        return self.browser_context

    async def exit_context(self, context: BrowserContext = None):
        print(
            "************************ ---Exiting the browser--- ************************")
        if context:
            await context.close()
        else:
            await self.browser_context.close()
        print(
            "************************ ---succesfully stopped the browser--- ************************")
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
            # print(
            #     "-------------------------------------------------------------------------")
            # print(
            #     "RUNNING -->> {action}_action using XPATH N* --> {number}".format(action=action.__name__, number=i+1))
            try:
                action_result = await action(selector=selector, **kwargs)
                # print(
                #     "SUCCESS -->> {action}_action using XPATH N* --> {number}".format(action=action.__name__, number=i+1))
                # print(
                #     "-------------------------------------------------------------------------")
                return action_result
            except NavigationTimeout:
                print("FAILED -->> trying next selector...")
        raise (ActionsFallback(
            "Could not handle this interaction fallback with the provided selectors"))
