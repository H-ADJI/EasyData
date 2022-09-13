'''
File: main.py
File Created: Monday, 18th July 2022 10:54:36 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
import asyncio
from datetime import datetime
import aiofiles
from playwright.async_api import async_playwright, BrowserContext
from playwright.async_api import Browser as Playwright_browser
from nsa.core.engine import Browser
from nsa.core.execute import GeneralPurposeScraper
import json
import os
from nsa.core.utils import dir_name
import shutil

# urls = [
#     "https://www.hespress.com/%D9%84%D8%A7%D8%B9%D8%A8-%D9%8A%D9%87%D8%AF%D9%8A-%D8%B3%D8%A7%D8%B9%D8%A9-%D8%B1%D9%88%D9%84%D9%8A%D9%83%D8%B3%D9%84%D9%85%D8%B4%D8%AC%D8%B9-1029780.html",
#     "https://www.hespress.com/%d9%85%d8%b5%d8%a7%d8%b9%d8%a8-%d9%81%d9%8a-%d9%82%d8%b7%d8%a7%d8%b9-%d8%a7%d9%84%d8%af%d9%88%d8%a7%d8%ac%d9%86-1028442.html",
#     "https://www.hespress.com/%d8%aa%d9%82%d8%b1%d9%8a%d8%b1-%d9%8a%d9%83%d8%b4%d9%81-%d8%aa%d8%af%d8%a7%d8%b9%d9%8a%d8%a7%d8%aa-%d9%81%d8%a7%d8%af%d8%ad%d8%a9-%d9%84%d9%85%d8%aa%d8%b6%d8%b1%d8%b1%d9%8a%d9%86-%d9%85%d9%86-%d8%ad-1027754.html",
#     "https://www.hespress.com/%d9%81%d8%a7%d8%b9%d9%84%d9%88%d9%86-%d9%8a%d9%8f%d8%ad%d8%b6%d8%b1%d9%88%d9%86-%d9%84%d9%8a%d9%88%d9%85-%d8%af%d8%b1%d8%a7%d8%b3%d9%8a-%d8%ad%d9%88%d9%84-%d8%a7%d9%84%d9%83%d9%8a%d9%81-1027916.html"
# ]


async def read_input_file(file_name="hespress_most_viewed_articles"):
    try:
        dir_name = "nsa/database/" + "articles_2022-08-30T11:00"
        async with aiofiles.open(f"{dir_name}/{file_name}.json", "r") as f:
            file_content = await f.read()
            data = json.loads(file_content)
        return data
    except Exception as e:
        print(f"/{dir_name}/{file_name}.json")
        print("didnt read file")
        return None


async def nsa(browser, objective, urls=None):
    # TODO: try handle parallelism using contexts
    scraper = GeneralPurposeScraper()
    data = await read_input_file()
    if data:
        urls = [article["url"] for article in data.get("most_viewed_articles")]
    # urls = ["https://www.hespress.com/%D8%A5%D8%B1%D8%AC%D8%A7%D8%A1-%D9%85%D8%AD%D8%A7%D9%83%D9%85%D8%A9-%D8%B4%D8%BA%D8%A8-%D9%8A%D8%AD%D8%B2%D9%86-%D8%B9%D8%A7%D8%A6%D9%84%D8%A7%D8%AA-%D8%A7%D9%84%D9%85%D8%AA%D8%A7%D8%A8%D8%B9-1031048.html",
    #         "https://www.hespress.com/%d8%b9%d8%b1%d9%8a%d8%b3-%d9%8a%d8%b9%d8%aa%d8%af%d9%8a-%d8%b9%d9%84%d9%89-%d8%b2%d9%88%d8%ac%d8%aa%d9%87-%d9%88%d8%b3%d8%b7-%d8%a7%d9%84%d8%b4%d8%a7%d8%b1%d8%b9-948140.html",
    #         "https://www.hespress.com/سفينتان-حربيتان-أمريكيتان-تعبران-مضي-1039179.html",
    #         "https://www.hespress.com/مطرح-للنفايات-يثير-انتقادات-في-إقليم-ت-1038713.html",
    #         "https://www.hespress.com/مع-المخرج-حسن-غنجة-1038476.html",
    #         "https://www.hespress.com/السعودية-تنفي-دخول-صحافي-إسرائيلي-إلى-1039393.html",
    #         ]
    await scraper.scrape(engine=browser, website="hespress", objective=objective, input_data={"categories_list": ["سياسة", "اقتصاد"], "articles_url": urls})


async def main():
    try:
        os.mkdir(dir_name)
    except:
        shutil.rmtree(dir_name)
        os.mkdir(dir_name)
    browser = Browser()
    tasks = []
    my_objectives = [
        "most_viewed_articles",
        "article_details",
        "article_details_raw",
    ]
    # await nsa(browser=browser, objective="most_viewed_articles")
    t1 = await nsa(browser=browser, objective="article_details")
    # t2 = nsa(browser=browser, objective="article_details_raw")
    # await asyncio.gather(t1, t2)
    await browser.exit_browser()
asyncio.run(main())
