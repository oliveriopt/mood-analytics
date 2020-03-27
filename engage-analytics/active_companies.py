#!/usr/bin/env python3

import logging.config
import newrelic.agent
import os

@newrelic.agent.background_task()

def task():
  # Logger
  from utils.data_connection.source_manager import Connector
  from utils.utilities import set_log_level, get_project_path
  from active_companies.src.workflows.validation import ActiveCompanies

  logging.config.fileConfig("%s/logging.ini" % get_project_path())
  set_log_level()

  conn = Connector(os.getenv("DB_USER"), os.getenv("DB_PASSWORD"), os.getenv("DB_HOST"), os.getenv("DB_PORT"))
  actv_companies = ActiveCompanies(db_connector=conn)

  # Active companies validation
  actv_companies.check_active_companies()

task()
