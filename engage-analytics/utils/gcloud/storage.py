import logging

from os import listdir, getenv
from google.cloud import storage
from utils.utilities import get_bucket_child_name

logger = logging.getLogger()

storage_client = storage.Client().from_service_account_json(json_credentials_path=getenv("GOOGLE_STORAGE_KEY_PATH"))
bucket = storage_client.get_bucket(getenv("GOOGLE_STORAGE_BUCKET", "mood-reports"))


class Storage:

    @staticmethod
    def upload_files(dir: str):
        """
        Upload files to GCP bucket.
        :param dir: absolute path to dir with files to be uploaded
        """
        files = [f for f in listdir(dir)]
        for file in files:
            local_file = dir + file
            blob = bucket.blob(f"{get_bucket_child_name()}/{file}")
            try:
                blob.upload_from_filename(local_file)
            except Exception as e:
                logger.error(msg=str(e))
            blob.make_public()
            logger.info(msg="File uploaded to GCloud bucket.")
