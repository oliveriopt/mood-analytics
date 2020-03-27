"""
Script with modules to alerts different and warnings
"""

import logging
import os
from slackclient import SlackClient

logger = logging.getLogger()


class AlertMessage:

    @staticmethod
    def send_slack_message(username: str, message: str) -> None:
        """
            :param username: username of slack
            :param message: message to send to slack
        """
        if os.getenv("APP_ENV") != "dev":
            token = os.getenv("SLACK_TOKEN")
            if token:
                sc = SlackClient(token)
                sc.api_call(
                    "chat.postMessage",
                    link_names=1,
                    channel="alerts_from_bots",
                    text=message,
                    username=username
                )

            else:
                logger.error(msg="SLACK_TOKEN not set in ENVs")