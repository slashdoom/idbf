#!/usr/bin/env python
###########################################################################
#
# Identity Database Framework (idbf)
#
# FILENAME:    idbf_scrubber.py
# DESCRIPTION: Time based scrubber script for iDbF
#
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

from lib.idbf_user_groups_db import *
import configparser
import logging
import os

# setup logging
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
config.read(os.path.join(os.path.dirname(__file__), "etc", "idbf_conf"))

try:
  # attempt DATABASE config read
  db_host = config["DATABASE"]["db_host"]
  db_user = config["DATABASE"]["db_user"]
  db_pass = config["DATABASE"]["db_pass"]
  db_name = config["DATABASE"]["db_name"]
except:
  # send error to logger
  logger.error("DATABASE connection settings not found in config")
  exit(0)

ug_db = idbf_user_groups_db(db_host,db_user,db_pass,db_name)

try:
  # attempt SCRUBBER config read
  scrub_day    = config["SCRUBBER"]["u2d_DAY"]
  scrub_hour   = config["SCRUBBER"]["u2d_HOUR"]
  scrub_minute = config["SCRUBBER"]["u2d_MINUTE"]
except:
  # send warning to logger
  logger.error("SCRUBBER settings not found in config")
  exit(0)

ug_db.ug_user_scrub(scrub_day, scrub_hour, scrub_minute)