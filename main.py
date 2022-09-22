'''
File: main.py
File Created: Monday, 18th July 2022 10:54:36 am
Author: KHALIL HADJI
-----
Copyright:  HENCEFORTH 2022
'''
from beanie import init_beanie
from nsa.api.router import router
from nsa.database.database import db
from beanie import init_beanie
from fastapi import FastAPI
from nsa.api.routes.authentication import create_super_user
from nsa.configs.configs import env_settings
from nsa.database.models import Project, User, Scraping_plan
from nsa.validation.validator import Scraping_plan_validator
# urls = ["https://www.hespress.com/%D8%A5%D8%B1%D8%AC%D8%A7%D8%A1-%D9%85%D8%AD%D8%A7%D9%83%D9%85%D8%A9-%D8%B4%D8%BA%D8%A8-%D9%8A%D8%AD%D8%B2%D9%86-%D8%B9%D8%A7%D8%A6%D9%84%D8%A7%D8%AA-%D8%A7%D9%84%D9%85%D8%AA%D8%A7%D8%A8%D8%B9-1031048.html",
#         "https://www.hespress.com/%d8%b9%d8%b1%d9%8a%d8%b3-%d9%8a%d8%b9%d8%aa%d8%af%d9%8a-%d8%b9%d9%84%d9%89-%d8%b2%d9%88%d8%ac%d8%aa%d9%87-%d9%88%d8%b3%d8%b7-%d8%a7%d9%84%d8%b4%d8%a7%d8%b1%d8%b9-948140.html",
#         "https://www.hespress.com/سفينتان-حربيتان-أمريكيتان-تعبران-مضي-1039179.html",
#         "https://www.hespress.com/مطرح-للنفايات-يثير-انتقادات-في-إقليم-ت-1038713.html",
#         "https://www.hespress.com/مع-المخرج-حسن-غنجة-1038476.html",
#         "https://www.hespress.com/السعودية-تنفي-دخول-صحافي-إسرائيلي-إلى-1039393.html",
#         ]


# async def nsa(browser, objective, urls=None):
#     scraper = GeneralPurposeScraper()

#     await scraper.scrape(engine=browser, website="hespress", objective=objective, input_data={"categories_list": ["سياسة", "اقتصاد"], "articles_url": urls})


# async def main():
#     browser = Browser()
#     await nsa(browser=browser, objective="article_details", urls=urls)
#     await browser.exit_browser()
# asyncio.run(main())
app = FastAPI()
app.include_router(router)


@ app.get("/")
async def root():
    return {"message": "Hello"}


@ app.on_event("startup")
async def on_startup():
    await init_beanie(
        database=db,
        document_models=[Project, User, Scraping_plan],
    )
    await create_super_user(email=env_settings.SUPER_USER_EMAIL, password=env_settings.SUPER_USER_PASSWORD)
    Scraping_plan_validator()