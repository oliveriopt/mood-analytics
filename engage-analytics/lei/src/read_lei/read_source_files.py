import json
import logging
import os
import io
import zipfile
import requests
import lei.src.read_lei.cons as cons

logger = logging.getLogger()


class ImportLeiFile:

    @staticmethod
    def read_link(type_lei_file: str, link_url: str) -> tuple:
        """
        Read url link for download file
        :param type_lei_file = "lei2" or "rr"
        :param link_url link to the file
        :return link_url: string of the link
        """

        url_response = requests.get(link_url)
        var_json = json.loads(url_response.content.decode(cons.FORMAT_DECODE))
        print(var_json)
        for (k, v) in var_json.items():
            print("Key: " + k)
            print("Value: " + str(v))
        try:
            link = var_json[cons.KEYS_JSON_FILE[0]][0][type_lei_file][cons.KEYS_JSON_FILE[2]][cons.KEYS_JSON_FILE[3]][
                cons.KEYS_JSON_FILE[4]]
            filename = link.split("/")[-1][:-4]
            logger.info(msg="LEI: Successfully Get link for " + type_lei_file + " file")

        except Exception as e:
            logger.error(msg="LEI: Error on exporting the link for " + type_lei_file + ": %s" % e)
            raise Exception(e)

        return link, filename


    @staticmethod
    def import_zip_file_unzip(path: str, filename, type_lei_file: str, url: str) -> str:
        """
        Make download of file lei2 or rr and save in /data_connection/ folder
        :param path : path of file
        :param filename : file name of file lei2 or rr
        :param type_lei_file = "lei2" or "rr"
        :param url: url for download the file
        """
        try:
            logger.info(msg="Getting LEI data_connection from %s" % url)
            extraction_path = "%s%s" % (path, cons.FOLDER_TO_STORAGE_DATA)
            file_path = "%s%s%s" % (path, cons.FOLDER_TO_STORAGE_DATA, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(msg="LEI: Old file " + type_lei_file + " was deleted")
            r = requests.get(url)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(extraction_path)
            logger.info(
                msg="LEI: Successfully Unziped file for " + type_lei_file + " file and stored on " + path + cons.FOLDER_TO_STORAGE_DATA)

        except Exception as e:
            logger.error(msg="LEI: Error on Unzipig file for " + type_lei_file + ": %s" % e)

        return file_path

    @staticmethod
    def run_import_unzip_file(path: str, type_lei_file: str) -> str:
        """
        Import the link, download the file of lei_2 or rr
        :param path : path of file
        :param type_lei_file = "lei2" or "rr"
        """

        url, filename = ImportLeiFile.read_link(type_lei_file, cons.PATH_LINK_URL_LEI_FILE)
        path_file = ImportLeiFile.import_zip_file_unzip(str(path), filename, type_lei_file, url)
        return path_file
