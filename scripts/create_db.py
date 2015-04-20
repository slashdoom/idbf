#!/usr/bin/env python3
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

# create idbf database
try: # check for existing database
  db_conn.database = db_name
  logger.warning("idbf_create_db database %s exists" % db_name)
except mysql.connector.Error as err:
  # database doesn't exist, attempt to create
  if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
    try:
      sql_query = ("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(db_name))
      db_cur.execute(sql_query)
      db_conn.database = db_name
      logger.debug("idbf_create_db create database %s successful" % db_name)
    except mysql.connector.Error as err:
        logger.error("idbf_create_db failed creating database: %s" % err)
        exit(1)
  else:
    logger.error("idbf_create_db failed creating database: %s" % err)
    exit(1)

# create user_to_ip table
try:
  # attempt to create idbf user_to_ip table
  sql_query = ("CREATE TABLE {}.user_to_ip ( "
               "id       BIGINT         NOT NULL AUTO_INCREMENT , PRIMARY KEY(id) , "
               "datetime TIMESTAMP      NOT NULL , "
               "user     VARCHAR(  50 ) NOT NULL , "
               "domain   VARCHAR( 100 ) NOT NULL , "
               "ip       VARCHAR(  39 ) NOT NULL, "
               "source   VARCHAR(  50 ) "
               ")").format(db_name)
  db_cur.execute(sql_query)
  logger.debug("idbf_create_db user_to_ip table created successfully")
except mysql.connector.Error as err:
  # log if user_to_ip table creation fails
  logger.error("idbf_create_db error creating %s.user_to_ip: %s" % (db_name, err))
  exit(1)

# create user_groups table
try:
  # attempt to create idbf user_groups table
  sql_query = ("CREATE TABLE {}.user_groups ( "
               "id       BIGINT NOT NULL AUTO_INCREMENT , PRIMARY KEY(id) , "
               "datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP , "
               "user     VARCHAR( 50 ) NOT NULL , "
               "domain   VARCHAR( 100 ) NOT NULL , "
               "groups   LONGTEXT "
               ")").format(db_name)
  db_cur.execute(sql_query)
  logger.debug("idbf_create_db user_groups table created successfully")
except mysql.connector.Error as err:
  # log if user_groups table creation fails
  logger.error("idbf_create_db error creating %s.user_groups: %s" % (db_name, err))
  exit(1)

# create idb_view view
try:
  # attempt to create idbf idb_view view
  sql_query = ("CREATE OR REPLACE VIEW idb_view AS "
               " SELECT "
               "  `user_to_ip`.`datetime` AS `datetime`, "
               "  `user_to_ip`.`ip`       AS `ip`, "
               "  `user_groups`.`user`    AS `user`, "
               "  `user_groups`.`domain`  AS `domain`, "
               "  `user_groups`.`groups`  AS `groups`, "
               "  `user_to_ip`.`source`   AS `source` "
               "  FROM (`user_to_ip` LEFT JOIN `user_groups` ON ("
               "  (`user_groups`.`user` = `user_to_ip`.`user`) AND "
               "  (`user_groups`.`domain` = `user_to_ip`.`domain`) ))"
               "  WHERE `user_to_ip`.`datetime` < "
               "   (NOW() - INTERVAL %s MINUTE - INTERVAL %s HOUR - INTERVAL %s DAY)")
  db_cur.execute(sql_query, (view_min, view_hour, view_day))
  logger.debug("idbf_create_db idb_view view created successfully")
except mysql.connector.Error as err:
  # log if idb_view virw creation fails
  logger.error("idbf_create_db error creating %s.idb_view: %s" % (db_name, err))

# create db user and assign privileges
# make sure user and pass are present and not root
if db_user and db_pass and (db_user != "root"):
  try:
    # attempt to create user
    sql_query = "CREATE USER %s@localhost IDENTIFIED BY %s"
    db_cur.execute(sql_query, (db_user, db_pass,))
    logger.debug("idbf_create_db user %s created" % db_user)
    # attempt to assign privileges
    sql_query = ("GRANT ALL PRIVILEGES ON {} . * TO %s@'localhost';").format(db_name)
    db_cur.execute(sql_query, (db_user,))
    logger.debug("idbf_create_db %s granted privileges" % db_user)
    # attempt to flush privileges
    db_conn.RefreshOptions.GRANT
    logger.debug("idbf_create_db privileges flushed")
  except mysql.connector.Error as err:
    # log if user creation fails
    logger.error("idbf_create_db error creating user %s: %s" % (db_user, err))

