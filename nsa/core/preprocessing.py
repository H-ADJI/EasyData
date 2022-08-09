'''
File: preprocessing.py
File Created: Monday, 8th August 2022 9:49:09 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''


from datetime import datetime
from typing import Any, List
import re
import nltk
from urllib.parse import unquote
# TODO: use translation dicts read from scraping plans


def data_processing(data: Any, processing_pipline: List[dict]):
    for processing in processing_pipline:
        processing_function = eval(processing.get("function"))
        preprocessing_inputs = processing.get("inputs", {})
        data = processing_function(data, **preprocessing_inputs)
    return data


def join_text(text_list: list, sep=' '):
    return sep.join(text_list)


def to_number(string_number):
    return int(string_number)


def strip_whitespaces(text: str):
    return text.strip()


def decode_url(url: str):
    return unquote(url)


def arabic_datetime(date: str, minutes_pattern: str = None, hours_pattern: str = None, days_pattern: str = None, months_pattern: str = None, year_pattern: str = None):
    arabic_months_mapping = {"يناير": 1,
                             "فبراير": 2,
                             "مارس": 3,
                             "أبريل": 4,
                             "ماي": 5,
                             "يونيو": 6,
                             "يوليو": 7,
                             "غشت": 8,
                             "سبتمبر": 9,
                             "أكتوبر": 10,
                             "نوفمبر": 11,
                             "ديسمبر": 12}
    date_elements = {}
    if minutes_pattern:
        minutes = re.search(minutes_pattern, date).group()
        date_elements["minute"] = int(minutes)

    if hours_pattern:
        hours = re.search(hours_pattern, date).group()
        date_elements["hour"] = int(hours)

    if days_pattern:
        day = re.search(days_pattern, date).group()
        date_elements["day"] = int(day)

    if months_pattern:
        month = re.search(months_pattern, date).group()
        matched_month = min([(m, nltk.edit_distance(month, m))
                            for m in arabic_months_mapping], key=lambda x: x[1])[0]
        month_number = arabic_months_mapping[matched_month]
        date_elements["month"] = int(month_number)

    if year_pattern:
        year = re.search(year_pattern, date).group()
        date_elements["year"] = int(year)

    return datetime(**date_elements).isoformat()


def extract_from_text(text: str, pattern: str):
    return re.search(pattern, text).group()


def remove_chars(text: str, characters_to_remove: str):
    translation = str.maketrans("", "", characters_to_remove)
    return text.translate(translation)
