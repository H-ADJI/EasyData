'''
File: main.py
File Created: Monday, 18th July 2022 10:54:36 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
import asyncio
from playwright.async_api import async_playwright, Playwright
from nsa.core.execute import scrape
import aiofiles
import json


async def run(playwright: Playwright):

    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = await chromium.launch(headless=False)
    page = await browser.new_page()
    data = await scrape(using=page, website="hespress", objectives=["article_links"], user_data={"categories_list": ["مجتمع", "اقتصاد"]})
    async with aiofiles.open("./nsa/database/hespress.json", "w") as f:
        await f.write(json.dumps(data))


async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())
