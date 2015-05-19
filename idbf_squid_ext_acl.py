#!/usr/bin/env python3
###########################################################################
#
# Identity Database Framework (idbf)
#
# FILENAME:    idbf_squid_ext_acl.py
# DESCRIPTION: script to provide Squid with usernames through
#              external_acl_type
#
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

import configparser
import logging
import mysql.connector
import os
import re
import sys

PYTHONUNBUFFERED = "true"

# open config file
config = configparser.ConfigParser()
# read db info
config.read(os.path.join(os.path.dirname(__file__), "etc", "idbf_conf"))

try:
  log_path = "{0}/{1}.log".format(config["LOGGING"]["path"],os.path.basename(__file__))
except:
  log_path = "{0}.log".format(os.path.basename(__file__))

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
fh = logging.FileHandler(log_path)
fh.setLevel(logging.WARNING)
fh_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')
fh.setFormatter(fh_format)
logger.addHandler(fh)

try:
  # attempt DATABASE config read
  db_host = config["DATABASE"]["db_host"]
  db_user = config["DATABASE"]["db_user"]
  db_pass = config["DATABASE"]["db_pass"]
  db_name = config["DATABASE"]["db_name"]
except:
  # send error to logger
  logger.error("idbf_squid_ext_acl DATABASE connection settings not found in config")
  exit(0)

try:
  for line in sys.stdin:
    # parse stdin for ip address
    re_ip = re.search('(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})',line)
    if (re_ip): # ip address found in stdin line
      try:
        # connect to mysql server
        db_conn = mysql.connector.connect(host=db_host,
                                          user=db_user,
                                          password=db_pass,
                                          database=db_name,
                                          buffered=True)
        # check mysql connection
      except mysql.connector.Error as err: # mysql connection error
        logger.error('idbf_squid_ext_acl MySQL error: %s', err)
        exit(0)

      # mysql connection successful, create cursor
      logger.debug("idbf_squid_ext_acl MySQL connected to %s" % db_name)
      db_cur = db_conn.cursor()
      # query idb_view view by ip
      sql_query = ("SELECT user, domain FROM idb_view WHERE ip=%s")
      db_cur.execute(sql_query, (re_ip.group(1),))
      # check that results were found in database
      if db_cur.rowcount == 1: # result found
        for (record) in db_cur:
          if (record[0] and record[1]): # username and domain are present
            print("OK user=" + record[0] + "@" + record[1])
          elif (record[0] and not record[1]): # only username is present
            print("OK user=" + record[0])
          else: # no username or domain present
            print("ERR")
      else: # no results or too many results found
        print("ERR")
      db_cur.close
      db_conn.close
      logger.debug("idbf_squid_ext_acl MySQL connection closed")
    else: # ip address not found in stdin line
      print("ERR")

except Exception as err:
  # send error to logger
  logger.error(err)
  exit(0)