import logging

import os

from google.oauth2 import service_account
from google.cloud import language

from utils.utilities import get_project_path, is_dev_env

logger = logging.getLogger()


class NLPGoogleClient:

    @staticmethod
    def open_client():
        """
        Open client for google service
        :return: protocol open
        """

        credentials_path = get_project_path() + '/keys/credentials.json'

        if not is_dev_env():
            credentials_path = os.getenv("GOOGLE_NLP_CREDENTIALS")

        google_client = language.LanguageServiceClient(
            credentials=service_account.Credentials.from_service_account_file(credentials_path))

        return google_client
