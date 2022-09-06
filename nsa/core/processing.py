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
import urllib.parse
# TODO: use translation dicts read from scraping plans


class Data_Processing:
    def __init__(self) -> None:
        self.white_spaces_pattern = re.compile(r"\s{2,}")
        self.arabic_noise = None
        self.arabic_letters_normalizing_pattern = None
        self.stop_words = None

    @staticmethod
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
                "nest22":"something_something"
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
                    "nest22":"something_something"
                }
            },
            "test":123
            }

        """
        if isinstance(data, list):
            for d in data:
                if Data_Processing.empty_data_to_None(d):
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

    def data_processing(self, data: Any, processing_pipline: List[dict]) -> Any:
        """Function responsible for calling processing function from the scraping plans

        Args:
            data (Any): data to be processed
            processing_pipline (List[dict]): list of function to be applied to data successively

        Returns:
            Any: Processed data
        """
        for processing in processing_pipline:
            # eval is dangerous
            processing_function = eval("self."+processing.get("function"))
            preprocessing_inputs = processing.get("inputs", {})
            data = processing_function(data, **preprocessing_inputs)
        return data

    @staticmethod
    def join_text(text_list: list, sep=' ') -> str:
        """ if the scraped text is spread over multiple html element tags the data will be extracted as a list so this function will combine it into a single text using a seperator 

        Args:
            text_list (list): the list containing the text to join
            sep (str, optional): separator used to join the text. Defaults to ' '.

        Returns:
            str: joined text
        """
        if isinstance(text_list, str):
            return text_list
        return sep.join(text_list)

    # TODO: add more punctuation
    @staticmethod
    def remove_punctuation(text: str, punctuation: str = "'()[]\{\}،*+=-_؟?.”;:!؛“") -> str:
        """Purge text from punctuation

        Args:
            text (str): text to be cleaned
            punctuation (_type_, optional): punctuation characters to remove. Defaults to "'()[]\{}،*+=-_؟?.”;:!؛“".

        Returns:
            str: punctuation free text 
        """
        translation = str.maketrans(punctuation, " "*len(punctuation))
        return text.translate(translation)

    @staticmethod
    def to_number(string_number) -> int:
        """Usually scraped data come as strings, this function will help turn numeric values into int object

        Args:
            string_number (_type_): numeric value to transform

        Returns:
            int: int equivelant of the string
        """
        return int(string_number)

    def strip_whitespaces(self, text: str) -> str:
        """remove  extra whitespaces from a text

        Args:
            text (str): text to be cleaned

        Returns:
            str: text with only single white spaces
        """
        text = re.sub(self.white_spaces_pattern, " ", text)
        return text.strip()

    @staticmethod
    def decode_url(url: str) -> str:
        """will decode utf-8 encoded characters

        Args:
            url (str): the encoded url

        Returns:
            str: decoded url
        """
        return urllib.parse.unquote(url)

    def extract_from_text(self, text: str, name: str, patterns: List[str]) -> str:
        """Extract sub-string fron text using a regex pattern

        Args:
            text (str): text to extract from
            patterns (List[str]): a list of patterns to support retry-ability

        Returns:
            str : the extracted text
        """
        if not self.__dict__.get(name):
            self.__dict__.update({name: [re.compile(pattern)
                                         for pattern in patterns]})
            print(f"JUST initiated ->>>>> {name}")
        for pattern in self.__dict__.get(name):
            searched_text = re.search(pattern, text)
            if searched_text:
                return searched_text.group()
            print(
                f"Could not match the pattern : {pattern} to the following text : {text}")
        return text

    @staticmethod
    def arabic_datetime(date: str, minutes_pattern: str = None, hours_pattern: str = None, days_pattern: str = None, months_pattern: str = None, year_pattern: str = None) -> str:
        """Help translate plain text arabic datetimes into an ISO format datetime
            it uses a translation mapping dictionary that should be hardcoded for every months variation
            TODO: find a work around to remove the hardcoded months mapping 

        Args:
            date (str): extracted date that will be normalized into ISO format
            minutes_pattern (str, optional): regex patterns to extract minutes from the text. Defaults to None.
            hours_pattern (str, optional): regex patterns to extract hours from the text. Defaults to None.
            days_pattern (str, optional): regex patterns to extract days from the text. Defaults to None.
            months_pattern (str, optional): regex patterns to extract months from the text. Defaults to None.
            year_pattern (str, optional): regex patterns to extract year from the text. Defaults to None.

        Returns:
            str: datetine as an ISO string format
        """
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

    @staticmethod
    def remove_chars(text: str, characters_to_remove: str):
        """purge text from a set of characters

        Args:
            text (str): text to be cleaned
            characters_to_remove (str): characters that will be removed

        Returns:
            str: clean text
        """
        translation = str.maketrans("", "", characters_to_remove)
        return text.translate(translation)

    def remove_arabic_noise(self, text):
        """remove some of the possible arabic characters that are considered as noise

        Args:
            text (str): text to be cleaned
        Returns:
            str: clean text
        """
        noise = """   ّ    | # Tashdid
                                َ    | # Fatha
                                ً    | # Tanwin Fath
                                ُ    | # Damma
                                ٌ    | # Tanwin Damm
                                ِ    | # Kasra
                                ٍ    | # Tanwin Kasr
                                ْ    | # Sukun
                                ـ     # Tatwil/Kashida
                            """
        if not self.arabic_noise:
            self.arabic_noise = re.compile(noise, re.VERBOSE)
            print("JUST initiated ->>>>>  arabic NOISE")

        text = re.sub(self.arabic_noise, '', text)
        return text

    def normalize_arabic_letters(self, text: str) -> str:
        """substitute some arabic characters into a standard form 
        example of characters that may have multiple forms :
        - ي and ى
        - ؤ and ء
        - ء and ئ
        ...

        Args:
            text (str): text to clean

        Returns:
            str: text with standard arabic characters
        """
        if not self.arabic_letters_normalizing_pattern:
            self.arabic_letters_normalizing_pattern = re.compile("[إأٱآا]")
            print("JUST initiated ->>>>>  arabic letters normalizer")

        text = re.sub(self.arabic_letters_normalizing_pattern, "ا", text)
        return text

    @staticmethod
    def remove_repeated_letters(text: str) -> str:
        """for every unique letter in our text we replace repeated (3+) letter with two letters
        this function doesn't take into consideration spelling correctness so it doesn't guarantee that the word will be 100% correct
        example :
        - eyeeeeeees becomes eyees
        - paralleel will become parallel 

        Args:
            text (str): _description_

        Returns:
            str: text with no repeated charcters
        """
        letters = set(text)
        for letter in letters:
            # TODO: keep words that have meaning even with repeated letters
            text = re.sub(f"{letter}"+"{3,}", 2*letter, text)
        return text

    def remove_stop_words(self, text: str) -> str:
        """remove stop words from the text
        - the used stop list https://github.com/mohataher/arabic-stop-words/blob/master/list.txt
        PS: before using them, the stop words have been pre-processed ( remove noise - normalize letters) 
        Args:
            text (str): text to clean from stop words

        Returns:
            str: text with no stop words 
        """
        if not self.stop_words:

            with open("./nsa/core/ar_stops.txt", "r") as f:
                self.stop_words: set[str] = set(f.read().split("\n"))
            print("JUST initiated ->>>>>  stop words")

        text_tokens = text.split(" ")
        clean_text_tokens = [
            w for w in text_tokens if w not in self.stop_words]
        clean_text = " ".join(clean_text_tokens)
        return clean_text
