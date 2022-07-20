'''
File: browser.py
File Created: Monday, 18th July 2022 10:54:07 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''

from typing import Literal
from playwright.async_api import async_playwright, BrowserContext, Page, Locator, Playwright
from nsa.errors.browser_errors import ActionsFallback, AttributeRetrievalError, WaitingError, ClickButtonError, HoverOverError, TabNotFound, TypingTextError, UploadFileError, UseKeyboardError
from playwright.async_api import TimeoutError as NavigationTimeout
from playwright.async_api import Browser as playwright_browser


async def launch_browser(playwright: Playwright, browser_configuration: dict, browser_type: Literal["chromium", "firefox", "webkit"]):
    browsers_choices = {"webkit": playwright.webkit,
                        "chromium": playwright.chromium, "firefox": playwright.firefox}
    browser = await browsers_choices.get(
        browser_type, playwright.chromium).launch()
    return browser


async def launch_context(browser: playwright_browser, context_config: dict, default_scraping_timeout: float, default_navigation_timeout: float):
    context: BrowserContext = await browser.new_context(context_config)
    context.set_default_timeout(timeout=default_scraping_timeout)
    context.set_default_navigation_timeout(timeout=default_navigation_timeout)
    return context


async def launch_page(context: BrowserContext, page_config=dict):
    page = await context.new_page(**page_config)
    return page


async def relocate(element: Page | Locator, selector: str = "*"):
    relocated_element = element.locator(selector)
    return relocated_element


async def handle_fallback(action, selectors: list[str], **kwargs):
    """Function that will handle the retry-ability of a browser action based on a list of xpaths

    Args:
        - action : the browser action that will be retried
        - selectors (list[str]): list of xpaths or css selectors
        - timeout : time treshold to wait before trying the next xpath
    """
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


async def visit_url(page: Page, url: str = "https://www.google.com/", **kwargs):
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
        await handle_fallback(action=click_action, selectors=selectors, click_count=count, **kwargs)
    except ActionsFallback:
        raise(ClickButtonError(
            "Unable to click the provided selectors"))


async def wait_for_something(element: Page | Locator, selectors: str, timeout: int = 30_000, **kwargs):
    waiting_action = element.wait_for_selector
    try:
        await handle_fallback(action=waiting_action, selectors=selectors, timeout=timeout, **kwargs)
    except ActionsFallback:
        raise WaitingError


async def scrape_attribute(element: Page | Locator, selectors: list[str], name: str, alias: str, match_all: bool = True, **kwargs):
    if match_all:
        data = []
        try:
            elements = await handle_fallback(action=relocate, selectors=selectors, element=element)
            elements_count = await elements.count()
            for i in range(elements_count):
                data.append(await elements.nth(i).get_attribute(name=name))
            # data = await element.get_attribute()
            return {alias: data}
        except ActionsFallback:
            raise(AttributeRetrievalError(
                "Unable to retrieve text with the provided selectors"))
    else:
        try:
            data = await handle_fallback(action=element.get_attribute, selectors=selectors, name=name, **kwargs)
            return {alias: data}
        except ActionsFallback:
            raise(AttributeRetrievalError(
                "Unable to retrieve attribute with the provided selectors"))


async def scrape_text(element: Page | Locator, selectors: list[str], alias: str, match_all: bool = True, reloc: bool = False, ** kwargs):
    if match_all:
        try:
            elements = await handle_fallback(action=relocate, selectors=selectors, element=element)
            data = await elements.all_text_contents()
            return {alias: data}
        except ActionsFallback:
            raise(AttributeRetrievalError(
                "Unable to retrieve text with the provided selectors"))
    else:
        try:
            data = await handle_fallback(action=element.text_content, selectors=selectors, **kwargs)
            return {alias: data}
        except ActionsFallback:
            raise(AttributeRetrievalError(
                "Unable to retrieve text with the provided selectors"))
