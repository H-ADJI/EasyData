'''
File: main.py
File Created: Monday, 18th July 2022 10:54:36 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
import asyncio
import aiofiles
from playwright.async_api import async_playwright, BrowserContext
from nsa.core.execute import GeneralPurposeScraper
import json

urls = [
    "https://www.hespress.com/%d8%a7%d9%84%d8%ad%d8%b7-%d9%85%d9%86-%d9%83%d8%b1%d8%a7%d9%85%d8%a9-%d8%a7%d9%84%d9%85%d8%ba%d8%b1%d8%a8%d9%8a%d8%a7%d8%aa-%d9%8a%d8%af%d9%81%d8%b9-%d8%ad%d9%82%d9%88%d9%82%d9%8a%d8%a7%d8%aa-%d8%a5-1027143.html",
    "https://www.hespress.com/%d8%aa%d9%82%d8%b1%d9%8a%d8%b1-%d9%8a%d9%83%d8%b4%d9%81-%d8%aa%d8%af%d8%a7%d8%b9%d9%8a%d8%a7%d8%aa-%d9%81%d8%a7%d8%af%d8%ad%d8%a9-%d9%84%d9%85%d8%aa%d8%b6%d8%b1%d8%b1%d9%8a%d9%86-%d9%85%d9%86-%d8%ad-1027754.html",
    "https://www.hespress.com/%d9%81%d8%a7%d8%b9%d9%84%d9%88%d9%86-%d9%8a%d9%8f%d8%ad%d8%b6%d8%b1%d9%88%d9%86-%d9%84%d9%8a%d9%88%d9%85-%d8%af%d8%b1%d8%a7%d8%b3%d9%8a-%d8%ad%d9%88%d9%84-%d8%a7%d9%84%d9%83%d9%8a%d9%81-1027916.html"
]


# async def read_input_file(file_name="targeted_links"):
#     async with aiofiles.open(f"./nsa/database/{file_name}.json", "r") as f:
#         file_content = await f.read()
#         data = json.loads(file_content)
#     return


async def nsa(context: BrowserContext, objective):
    # TODO: try handle parallelism using contexts
    page = await context.new_page()
    await GeneralPurposeScraper.scrape(using=page, website="hespress", objective=objective, user_data={"categories_list": ["سياسة", "اقتصاد"], "articles_url": urls})


async def main():
    tasks = []
    async with async_playwright() as playwright:
        chromium = playwright.chromium  # or "firefox" or "webkit".
        browser = await chromium.launch(headless=False)
        context = await browser.new_context()
        my_objectives = [
            # "categories",
            "article_details",
            # "most_viewed_articles"
        ]
        for obj in my_objectives:
            tasks.append(asyncio.create_task(
                nsa(context=context, objective=obj)))
        await asyncio.gather(*tasks)
asyncio.run(main())
