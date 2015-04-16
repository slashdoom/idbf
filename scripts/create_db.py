#!/usr/bin/env python
###########################################################################
#
# Identity Database Framework (idbf)
#
# FILENAME:    idbf_create_db.py
# DESCRIPTION: script to create iDbF mysql database
#
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

import configparser
import logging
import mysql.connector
import os

PYTHONUNBUFFERED = "true"

#setup logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# setup console logging handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')
ch.setFormatter(ch_format)
logger.addHandler(ch)
# setup file logging handler
fh = logging.FileHandler("{0}.log".format(__name__))
fh.setLevel(logging.WARNING)
fh_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')
fh.setFormatter(fh_format)
logger.addHandler(fh)

# open config file
config = configparser.ConfigParser()
# read db info
config.read(os.path.join(os.path.dirname(__file__), "..", "etc", "idbf_conf"))

try:
  # attempt DATABASE config read
  db_host =      config["DATABASE"]["db_host"]
  db_user =      config["DATABASE"]["db_user"]
  db_pass =      config["DATABASE"]["db_pass"]
  db_name =      config["DATABASE"]["db_name"]
  db_root_user = config["DATABASE"]["db_root_user"]
  db_root_pass = config["DATABASE"]["db_root_pass"]
except:
  # send error to logger
  logger.error("DATABASE connection settings not found in config")
  exit(0)

# connect to mysql server
try:
  db_conn = mysql.connector.connect(host=db_host,
                                    user=db_root_user,
                                    password=db_root_pass,
                                    buffered=True)
# check mysql connection
except mysql.connector.Error as err: # mysql connection error
  logger.error('idbf_user_groups_db MySQL error: %s', err)
  exit(0)

# mysql connection successful, create cursor
logger.debug("idbf_create_db MySQL connected to %s" % db_host)
db_cur = db_conn.cursor()