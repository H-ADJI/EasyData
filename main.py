'''
File: main.py
File Created: Monday, 18th July 2022 10:54:36 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext
from nsa.core.execute import GeneralPurposeScraper
import aiofiles
import json
import random


async def nsa(context: BrowserContext, objective):
    # TODO: try handle parallelism using contexts
    page = await context.new_page()
    data = await GeneralPurposeScraper.scrape(using=page, website="hespress", objective=objective, user_data={"categories_list": ["سياسة", "مجتمع", "اقتصاد"]})
    async with aiofiles.open(f"./nsa/database/hespress_{datetime.now().isoformat(timespec='seconds')}.json", "w") as f:
        await f.write(json.dumps(data, ensure_ascii=False))


async def main():
    tasks = []
    async with async_playwright() as playwright:
        chromium = playwright.chromium  # or "firefox" or "webkit".
        browser = await chromium.launch(headless=False)
        context = await browser.new_context()
        my_objectives = ["article_links", "most_viewed", "test_do_until"]
        for obj in my_objectives:
            tasks.append(asyncio.create_task(
                nsa(context=context, objective=obj)))
        await asyncio.gather(*tasks)
asyncio.run(main())
