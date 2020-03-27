#!/usr/bin/env python3

import time
import sys
import shutil
import logging.config

from src.lei.src.read_path import *
from src.lei.src.read_source_files import ImportLeiFile
from src.lei.src.read_transform_file import *
from src.lei.src.split_file import *
from src.lei.src.inject_sql import *
from src.utilities import set_log_level, get_project_path

# Logger
logging.config.fileConfig("%s/logging.ini" % get_project_path())
set_log_level()

start = time.time()
sys.setrecursionlimit(100000)

path = str(TakePath.define_path())

### IMPORT FILE AND DOWNLOAD THE FILE TO /DATA/ FOLDER
pathFile_lei2 = ImportLeiFile.run_import_unzip_file(path, type_lei_file="lei2")
pathFile_rr = ImportLeiFile.run_import_unzip_file(path, type_lei_file="rr")

## SPLIT BIG FILE JSON
Split.split_json(source_filepath=pathFile_lei2, dest_folder=path + cons.FOLDER_TO_STORAGE_DATA,
                 split_file_prefix=path + cons.FOLDER_TO_STORAGE_DATA \
                                   + cons.PREFIX_TEMPORARY_FILE, records_per_file=cons.REGISTERS_PER_FILE,
                 type_file="lei2")
Split.split_json(source_filepath=pathFile_rr, dest_folder=path + cons.FOLDER_TO_STORAGE_DATA,
                 split_file_prefix=path + cons.FOLDER_TO_STORAGE_DATA \
                                   + cons.PREFIX_TEMPORARY_FILE_RR, records_per_file=10000, type_file="rr")

list_file = sorted(os.listdir(path + cons.FOLDER_TO_STORAGE_DATA))[1:]
list_file_rr = [s for s in list_file if "rr" in s]
list_file = list_file[0:len(list_file) - len(list_file_rr)]

conn = Connector(user="root", pw="", host="localhost", database=cons.DATABASE_NAME)
conn.open_connection()

### READ FILES JSON ALREADY SPLITTED
for i in list_file:

    first_step = False
    entity, other_names, other_add = ParserJSON.read_files(path + cons.FOLDER_TO_STORAGE_DATA + str(i))
    if i != "test_file_00": first_step = True
    InjectSQLtoDB.inject_to_db_entity(conn, entity, other_names, other_add, first_step)

for i in list_file_rr:
    relationships = ParserJSON.read_files_rr(path + cons.FOLDER_TO_STORAGE_DATA + str(i))
    InjectSQLtoDB.inject_to_db_rr(conn, relationships)

## DELETE TEMP FILE
shutil.rmtree("%s%s" % (path, cons.FOLDER_TO_STORAGE_DATA))

logger.info(msg="Process time: " + str((time.time() - start)) + " sec.")
conn.close_connection()
