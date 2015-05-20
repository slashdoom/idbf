#!/usr/bin/env python3
###########################################################################
#
# Identity Database Framework (idbf)
#
# FILENAME:    idbf_update_idb_view.py
# DESCRIPTION: script to update the idb_view table of the idbf database to
#               change lookup retention settings
#
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

import configparser
import logging
import mysql.connector
import os

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

try:
  # attempt VIEW config read
  view_day  = config["VIEW"]["view_DAY"]
  view_hour = config["VIEW"]["view_HOUR"]
  view_min  = config["VIEW"]["view_MINUTE"]
except:
  # send error to logger
  logger.error("VIEW settings not found in config")
  exit(1)

# connect to mysql server
try:
  db_conn = mysql.connector.connect(host=db_host,
                                    user=db_root_user,
                                    password=db_root_pass,
                                    buffered=True)
# check mysql connection
except mysql.connector.Error as err: # mysql connection error
  logger.error('idbf_user_groups_db MySQL error: %s', err)
  exit(1)

# mysql connection successful, create cursor
logger.debug("idbf_create_db MySQL connected to %s" % db_host)
db_cur = db_conn.cursor()

# create or replace idb_view view
try:
  # attempt to create idbf idb_view view
  sql_query = ("CREATE OR REPLACE VIEW idb_view AS "
               " SELECT "
               "  `user_to_ip`.`datetime` AS `v_datetime`, "
               "  `user_to_ip`.`ip`       AS `v_ip`, "
               "  `user_groups`.`user`    AS `v_user`, "
               "  `user_groups`.`domain`  AS `v_domain`, "
               "  `user_groups`.`groups`  AS `v_groups`, "
               "  `user_to_ip`.`source`   AS `v_source` "
               "  FROM (`user_to_ip` LEFT JOIN `user_groups` ON ("
               "  (`user_groups`.`user` = `user_to_ip`.`user`) AND "
               "  (`user_groups`.`domain` = `user_to_ip`.`domain`) ))"
               "  WHERE `user_to_ip`.`datetime` > "
               "   (NOW() - INTERVAL %s MINUTE - INTERVAL %s HOUR - INTERVAL %s DAY)")
  db_cur.execute(sql_query, (view_min, view_hour, view_day))
  logger.debug("idbf_create_db idb_view view created successfully")
except mysql.connector.Error as err:
  # log if idb_view virw creation fails
  logger.error("idbf_create_db error creating %s.idb_view: %s" % (db_name, err))

