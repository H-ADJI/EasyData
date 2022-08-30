'''
File: preprocessing.py
File Created: Monday, 8th August 2022 9:49:09 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''


from datetime import datetime
from typing import Any, Dict, List
import re
import nltk
from urllib.parse import unquote

# TODO: use translation dicts read from scraping plans


def empty_data_to_None(data):
    """Example:
    ========================
    This dictionary :
    ========================
    {
    "so_nested":{
        "nested1_should_be_None":{
            "nest11":"None",
            "nest12":"None"
        },
        "nested1_should_stay_as_is":{
            "nest21":"None",
            "nest22":"haha"
        }
    },
    "test":123,
    "foo":{
        "foo1":"None",
        "foo2":"None"
    },
    "bar":{
        "bar1":"None",
        "bar2":5
    }
    }
    ========================
    will be transformed to :
    ========================

        {
        "bar":{
            "bar1":"None",
            "bar2":5
        },
        "foo":"None",
        "so_nested":{
            "nested1_should_be_None":"None",
            "nested1_should_stay_as_is":{
                "nest21":"None",
                "nest22":"haha"
            }
        },
        "test":123
        }

    """
    if isinstance(data, list):
        for d in data:
            if empty_data_to_None(d):
                return data

        return None
    flag = 0
    if isinstance(data, dict):
        dict_items = data.items()
        for k, v in dict_items:
            if v == {} or v == []:
                continue
            elif v != None:
                flag = 1
        if flag == 1:
            return data
        else:
            return None


def data_processing(data: Any, processing_pipline: List[dict]):
    for processing in processing_pipline:
        processing_function = eval(processing.get("function"))
        preprocessing_inputs = processing.get("inputs", {})
        data = processing_function(data, **preprocessing_inputs)
    return data


def join_text(text_list: list, sep=' '):
    if isinstance(text_list, str):
        return text_list
    return sep.join(text_list)


# TODO: add more punctuation
def remove_punctuation(text: str, punctuation: str = "'()[]\{\}،*+=-_؟?.”;:!؛“"):
    translation = str.maketrans(punctuation, " "*len(punctuation))
    return text.translate(translation)


def to_number(string_number):
    return int(string_number)


def strip_whitespaces(text: str):
    text = re.sub("\s{2,}", " ", text)
    return text.strip()


def decode_url(url: str):
    return unquote(url)


def extract_from_text(text: str, patterns: List[str]):
    for pattern in patterns:
        searched_text = re.search(pattern, text)
        if searched_text:
            return searched_text.group()
        print(
            f"Could not match the pattern : {pattern} to the following text : {text}")
    return text


def arabic_datetime(date: str, minutes_pattern: str = None, hours_pattern: str = None, days_pattern: str = None, months_pattern: str = None, year_pattern: str = None):
    # TODO: split into two functions one for matching date elements one for mapping them to datetime
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


def remove_chars(text: str, characters_to_remove: str):
    translation = str.maketrans("", "", characters_to_remove)
    return text.translate(translation)


def remove_arabic_noise(text):
    noise = re.compile("""   ّ    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                            ـ     # Tatwil/Kashida
                         """, re.VERBOSE)
    text = re.sub(noise, '', text)
    return text


def normalize_arabic_letters(text):
    text = re.sub("[إأٱآا]", "ا", text)
    # text = re.sub("ى", "ي", text)
    # text = re.sub("ؤ", "ء", text)
    # text = re.sub("ئ", "ء", text)
    # text = re.sub("ك", "hh",text)
    # text = re.sub("ة", "ه", text)
    return text


def remove_repeated_letters(text):
    try:
        letters = set(text)
        for letter in letters:
            # TODO: keep words that have meaning even with repeated letters
            text = re.sub(f"{letter}"+"{2,}", letter, text)
    except:
        print(f"{letter}"+"{2,}")
    return text


def remove_stop_words(text: str):
    with open("./nsa/core/ar_stops.txt", "r") as f:
        stop_words: set[str] = set(f.read().split("\n"))
    text_tokens = text.split(" ")
    clean_text_tokens = [w for w in text_tokens if w not in stop_words]
    clean_text = " ".join(clean_text_tokens)
    return clean_text
