import logging
import warnings

import os

import lei.src.mapping_duns_lei_engage.cons as cons
import time
import html
import pandas as pd

from Levenshtein import distance
from fuzzywuzzy import process

from utils.data_connection.source_manager import Connector

logger = logging.getLogger()
warnings.filterwarnings("ignore", category=pymysql.Warning)


def create_connection(user: str, pw: str, host: str, database: str):
    """
    Create connection with database
    :param database : name of database
    :return link: connection with database
    """
    conn = Connector(user=user, pw=pw, host=host, database=database, port=3306)
    return conn


def create_list_from_query(conn, database: str, table: str, number_id: str, name_company: str,
                           is_enable: bool) -> tuple:
    """
    :param database:
    :param table:
    :param number_id:
    :param name_company:
    :param is_enable:
    :return:
    """

    conn.open_connection()
    if is_enable:
        query = 'SELECT ' + number_id + ', ' + name_company + ' FROM ' + \
                database + '.' + table + ' WHERE ' + table + '.is_enabled=1;'
        q = conn.select_query(query)
    else:
        query = 'SELECT ' + number_id + ', ' + name_company + ' FROM ' + \
                database + '.' + table + ';'
        q = conn.select_query(query)
    q = (list(q))
    names = []
    number = []
    for i in q:
        if i[1] is not None:
            names.append(html.unescape(str(i[1]).lower()))
            number.append(i[0])
    if is_enable:
        Q = []
        for s in names:
            j = s.split(" ")
            for k in cons.LIST_REMOVE_SPECIAL_STINGS:
                if k in j:
                    j.remove(k)
            st = ' '.join(j)
            Q.append(st)
        names = Q

    conn.close_connection()
    return names, number


def closest(word, lst, id):
    k = 0
    match = []
    for i in lst:
        split_string = i.split()
        for j in split_string:
            dis = distance(word, j)
            if dis <= 1: match.append([i, id[k]])
        k = k + 1
    return match


def refine_search(word, lst):
    names = [item[0] for item in lst]
    x = process.extract(" " + word + " ", names, limit=10)
    names_refine = [item[0] for item in x]
    return names_refine


def is_in(word: str, lst: list, id: list) -> list:
    k = 0
    match = []
    for i in lst:
        if word in i: match.append([i, id[k]])
        k = k + 1
    return match


start = time.time()

conn = create_connection(user=os.getenv("DB_USER"), pw=os.getenv("DB_PASSWORD"), host=os.getenv("DB_HOST"),
                         database=cons.DATABASE_NAME)
names_lei, number_lei = create_list_from_query(conn, cons.DATABASE_NAME, cons.LEI_ENTITIES_TABLE, "lei_2",
                                               "entity_legalname", is_enable=False)

conn = create_connection(user=os.getenv("DB_USER"), pw=os.getenv("DB_PASSWORD"), host=os.getenv("DB_HOST"),
                         database=cons.DATABASE_NAME)
company_name_duns, number_duns = create_list_from_query(conn, cons.DATABASE_NAME, cons.DUNS_TABLE, "duns_id",
                                                        "company_name", is_enable=False)

conn = create_connection(user=os.getenv("DB_USER"), pw=os.getenv("DB_PASSWORD"), host=os.getenv("DB_HOST"),
                         database=cons.DATABASE_NAME_MOOD)
company_name_eng, number_eng = create_list_from_query(conn, cons.DATABASE_NAME_MOOD, cons.MOOD_TABLE, "id", "name",
                                                      is_enable=True)
M = 0
L = 0
R = 0
resume = pd.DataFrame(columns=["Name_Engage", "Number_LEI", "Number_DUNS"])
for i in range(len(company_name_eng)):

    if len(company_name_eng[i]) > 0:
        print("=" * 30)
        print(company_name_eng[i], number_eng[i])
        lei_search = is_in(company_name_eng[i], names_lei, number_lei)
        duns_search = is_in(company_name_eng[i], company_name_duns, number_duns)

        resume = resume.append(pd.Series([company_name_eng[i], len(lei_search), len(duns_search)]), ignore_index=True)
print("Total Number of companies ", len(company_name_eng))
print("Total Number of companies with lei_2 ", M)
print("Total Number of companies with duns ", L)
print("Total Number of companies with duns & lei_2 ", R)
pd.set_option('display.max_columns', 40)
resume.to_csv("test.csv")
print(resume)
print(str(time.time() - start) + " seconds")
