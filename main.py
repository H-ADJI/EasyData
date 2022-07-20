'''
File: main.py
File Created: Monday, 18th July 2022 10:54:36 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
import asyncio
from playwright.async_api import async_playwright, Playwright
from nsa.core.execute import execute_plam
from yaml import load, SafeLoader
import aiofiles
import json
with open("./nsa/scraping_plan/hespress.yml", "r") as yml:
    inputs_dict = load(yml, Loader=SafeLoader)


async def run(playwright: Playwright):

    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = await chromium.launch(headless=False)
    page = await browser.new_page()
    data = await execute_plam(page=page, plan=inputs_dict["hespress"])
    async with aiofiles.open("./nsa/database/hespress.json", "a") as f:
        await f.write(json.dumps(data))


async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())
