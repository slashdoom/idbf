#!/usr/bin/env python3
###########################################################################
#
# Identity Database Framework (idbf)
#
# FILENAME:    idbf_ise_byod.py
# DESCRIPTION: iDbF ISE BYOD Event Parser
#
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

from lib.idbf_user_to_ip_db import *
from lib.idbf_ad_format import *
import configparser
import datetime
import logging
import os
import re
import sys
import time

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
  logger.error("DATABASE connection settings not found in config")
  exit(0)

try:
  # attempt DOMAIN config read
  domains = dict(config.items("DOMAIN"))
except:
  # send warning to logger
  logger.warning("DOMAIN settings not found in config")

u2i_db = idbf_user_to_ip_db(db_host,db_user,db_pass,db_name)

try:
  for line in sys.stdin:

    # search for correct network identifier:
    matchNetID = re.search(r'.*Airespace\-Wlan\-Id=124.*', line)
    # search syslog message for User-Name attribute
    matchObj = re.search(r'User-Name=([a-zA-Z0-9\\\\]+),', line)

    if matchObj and matchNetID:
      # store username
      log_username = str(matchObj.group(1)).lower()
      # MAC regex:
      mac = re.compile("([a-fA-F0-9]{2}[:|\-]?){6}")
      # computername regex (fqdn):
      cn = re.compile("\.")

      if not mac.match(log_username) and not cn.match(log_username):
        # check username for domain
        matchObj = re.search(r'([a-z0-9]+)[\\\\]+([a-z0-9]+)', log_username)

        # if domain is found separate username and domain
        if matchObj:
          logger.debug("idbf_ise_byod.py - username with domain found.  %s\\%s" % (str(matchObj.group(1)).upper(),
                                                                                   str(matchObj.group(2)).lower()))
          log_domain = str(matchObj.group(1)).lower()
          log_username = str(matchObj.group(2)).lower()
          # if domain not found it in username use default
        else:
          log_domain = config["DEFAULT"]["domain"]
          logger.debug("idbf_ise_byod.py - username without domain found.  Assuming %s\\%s" % (log_domain, log_username))
        # Find the IP address provided in the syslog msg:
        matchIP = re.search(r'Framed-IP-Address=([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}),', line)

        if matchIP:
          logger.info("Device IP address found. %s" % (str(matchIP.group(1))))
          ip = str(matchIP.group(1))
          # create radius acct packet if it found a match:
          if ip == "0.0.0.0":
            logger.warning("idbf_ise_byod.py - invalid IP address (%s) found for user %s\\%s." % (ip,
                                                                                                  log_domain.upper(),
                                                                                                  log_username))
          else:
            logger.debug("idbf_ise_byod.py - calling radacct(). [%s, %s, %s]" % (log_domain.upper(), log_username, ip))
            u2i_db.u2i_user_add(time.strftime("%Y-%m-%d %H:%M:%S"),
                                adf_user(log_username),
                                adf_domain(log_domain,domains),
                                ip,
                                ("ise (BYODNet)"))

      else:
        logger.debug("idbf_ise_byod.py - detected computer name or MAC address. skipping: %s" % log_username)

except Exception as err:
  # send error to logger
  logger.error(err)
  exit(0)