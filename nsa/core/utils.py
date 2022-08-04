'''
File: utils.py
File Created: Wednesday, 3rd August 2022 5:20:58 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''


def append_without_duplicate(data: list, target: list):
    if data == None:
        data = []
    target.extend(data)
    union_without_duplicates = []
    if target:
        for d in target:
            if d not in union_without_duplicates:
                union_without_duplicates.append(d)
        return union_without_duplicates
    return []
