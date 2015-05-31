#!/usr/bin/env python3
###########################################################################
#
# Identity Database Framework (idbf)
#
# FILENAME:    idbf_ufdb_execuser.py
# DESCRIPTION: script to provide ufdbguard with usernames through
#              execuserlist
#
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

import configparser
import getopt
import logging
import mysql.connector
import os
import sys

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
  logger.error("idbf_ufdb_execuser DATABASE connection settings not found in config")
  exit(1)

def main(argv):
  # define argument variables
  domain = ''
  group = ''
  user = ''
  # attempt to get arguments
  try:
    opts, args = getopt.getopt(argv,"d:g:u:",["domain=","group=","user="])
  # invalid arguments found
  except getopt.GetoptError:
    logger.error("idbf_ufdb_execuser invalid arguments")
    exit(2)
  # valid arguments found
  for opt, arg in opts:
    # help argument found
    if opt in ("-h", "--help"):
      print('idbf_ufdb_execuser.py -d <domain> -g <group> or -u <username>')
      exit()
    # domain argument found, assign variable
    elif opt in ("-d", "--domain"):
      domain = arg
    # group argument found, assign variable
    elif opt in ("-g", "--group"):
      group = arg
    # user argument found, assign variable
    elif opt in ("-u", "--user"):
      user = arg
  # ensure that a domain and group or user are found
  if domain and (group or user):
    if user: # user query, print username and exit
      print("%s@%s" % (user,domain))
    elif group:
      try:
        # connect to mysql server
        db_conn = mysql.connector.connect(host=db_host,
                                          user=db_user,
                                          password=db_pass,
                                          database=db_name,
                                          buffered=True)
        # mysql connection successful, create cursor
        logger.debug("idbf_ufdb_execuser.py MySQL connected to %s" % db_name)
        db_cur = db_conn.cursor()
        # query user_groups
        sql_query = ("SELECT user, domain FROM user_groups WHERE groups LIKE '%|{}|%'").format(domain+"\\\\\\\\"+group)
        db_cur.execute(sql_query)
        # print username list from results
        for (s_user, s_domain) in db_cur:
          print("%s@%s" % (s_user, s_domain))
        # close out sql connector
        db_cur.close()
        db_conn.close()
    # invalid argument sequence, exit program
    else:
      logger.error("idbf_ufdb_execuser domain and group or user not found")
      sys.exit(2)

# call program with arguments
if __name__ == "__main__":
   main(sys.argv[1:])