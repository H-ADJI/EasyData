'''
File: browser.py
File Created: Monday, 18th July 2022 10:54:07 am
Author: KHALIL HADJI
-----
Copyright:  HENCEFORTH 2022
'''
from abc import abstractmethod
from typing import Literal, Protocol
from playwright.async_api import BrowserContext, Page, Locator, Playwright
from nsa.errors.browser_errors import ActionsFallback, AttributeRetrievalError, WaitingError, ClickButtonError, UseKeyboardError
from playwright.async_api import TimeoutError as NavigationTimeout
from playwright.async_api import Browser as playwright_browser


class Engine(Protocol):
    # Protocols replace ABCs: where ABCs are run-time checks, Protocols provide static-checking, and can take place before run-time.

    @abstractmethod
    async def visit_url():
        raise NotImplementedError

    @abstractmethod
    async def scrape_page():
        raise NotImplementedError


class Browser(Engine):
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

    async def relocate(element:  Locator, selector: str = "*"):
        relocated_element = element.locator(selector)
        return relocated_element

    @staticmethod
    async def handle_fallback(action, selectors: list[str] = None, **kwargs):
        """Function that will handle the retry-ability of a browser action based on a list of xpaths

        Args:
            - action : the browser action that will be retried
            - selectors (list[str]): list of xpaths or css selectors
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

    async def click(element: Page | Locator, selectors, count: int = 1, **kwargs):
        """Click the element(s) matching the selector(s)

        Args:
            - element (Page | Locator): a web browser element, could be either a tab (Page) or a Locator
            - selectors (list[str]): list of xpaths or css selectors
            - count (int, optional): number of click to execute. Defaults to 1.

        """
        click_action = element.click
        try:
            await Browser.handle_fallback(action=click_action, selectors=selectors, click_count=count, **kwargs)
        except ActionsFallback:
            raise(ClickButtonError(
                "Unable to click the provided selectors"))

    async def use_keyboard(element: Page | Locator, keys: list[str],   selectors: list[str] = None, delay: float = 200, **kwargs):
        """Send keystrokes to the element(s) matching the selector(s)

        Args:
            - element (Page | Locator): a web browser element, could be either a tab (Page) or a Locator
            - selectors (list[str]): list of xpaths or css selectors
            - keys (list[str]): keyboard keys to use  <https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/key/Key_Values#modifier_keys>'
            - delay (float, optional): time delay between each button press and release. Defaults to 0.


        """
        type_action = element.press
        try:
            for key in keys:
                await Browser.handle_fallback(action=type_action, selectors=selectors, key=key, delay=delay, **kwargs)
        except ActionsFallback:
            raise(UseKeyboardError(
                "Unable to send keyboard keypress to element with the provided selectors"))

    async def wait_for_something(element: Page | Locator, selectors: list[str], timeout: int = 30_000, **kwargs):
        waiting_action = element.wait_for_selector
        try:
            await Browser.handle_fallback(action=waiting_action, selectors=selectors, timeout=timeout, **kwargs)
        except ActionsFallback:
            raise WaitingError

    async def scrape_page(element: Page | Locator, selectors: list[str], data_to_get: list[dict], include_order: bool = False, **kwargs):
        data_to_return = []
        try:
            elements = await Browser.handle_fallback(action=Browser.relocate, selectors=selectors, element=element)
        except ActionsFallback:
            raise(AttributeRetrievalError(
                "Unable to locate the element(s) with provided selectors"))
        elements_count = await elements.count()
        for i in range(elements_count):
            current_element_data = {}
            current_element = elements.nth(i)
            if include_order:
                current_element_data["#"] = i + 1
            for d in data_to_get:
                current_element = elements.nth(i)
                if "relocate" in d:
                    current_element = current_element.locator(
                        d.get("relocate"))
                if d.get("kind") == "attribute":
                    attribute = await current_element.get_attribute(name=d.get("name"))
                    current_element_data[d.get("alias")] = attribute
                elif d.get("kind") == "text":
                    text = await current_element.text_content()
                    current_element_data[d.get("alias")] = text
            data_to_return.append(current_element_data)
        return data_to_return
