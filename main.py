'''
File: main.py
File Created: Monday, 18th July 2022 10:54:36 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
import asyncio
from playwright.async_api import async_playwright, BrowserContext
from nsa.core.execute import GeneralPurposeScraper


async def nsa(context: BrowserContext, objective):
    # TODO: try handle parallelism using contexts
    page = await context.new_page()
    await GeneralPurposeScraper.scrape(using=page, website="hespress", objective=objective, user_data={"categories_list": ["سياسة", "مجتمع", "اقتصاد"]})


async def main():
    tasks = []
    async with async_playwright() as playwright:
        chromium = playwright.chromium  # or "firefox" or "webkit".
        browser = await chromium.launch(headless=False)
        context = await browser.new_context()
        my_objectives = ["most_viewed_articles"]
        for obj in my_objectives:
            tasks.append(asyncio.create_task(
                nsa(context=context, objective=obj)))
        await asyncio.gather(*tasks)
asyncio.run(main())
