'''
File: data_validation.py
File Created: Thursday, 11th August 2022 2:17:32 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''


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
    if isinstance(data,list):
        for d in data:
            if  empty_data_to_None(d) :
                return data
            
        return None 
    flag = 0
    ###################################################
    if isinstance(data,dict):
        dict_items = data.items()
        for k, v in dict_items:
            if v == {} or v == []:
                continue
            elif v != None:
                flag = 1
        if flag == 1 :
            return data
        else :
            return None
    ###################################################