#!/usr/bin/env python3

from utils.alerts.slack_message import AlertMessage
from utils.utilities import generate_slack_message, get_project_path


class NotificationManager:
    """
    Notifications manager.
    It encapsulates the notification system used.
    """

    @staticmethod
    def notify_logging_event() -> None:
        """
        Notifies the system in use, using the last logging message.
        :return:
        """
        log_file = open("%s/engage-analytics.log" % get_project_path(), 'r').readlines()

        msg = generate_slack_message(message_heading="New Job Finished",
                                     status=False,
                                     logging_message=log_file[-1:][0])
        AlertMessage.send_slack_message("Active Companies Workflow", msg)
