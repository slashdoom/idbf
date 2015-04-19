#!/usr/bin/env python3
###########################################################################
#
# Identity Database Framework (iDbF)
#
# FILENAME:    idbf_windc.py
# DESCRIPTION: iDbF Windows DC eventlog parser
# 
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

from lib.idbf_user_to_ip_db import *
from lib.idbf_ad_format import *
import configparser
import logging
import os
import re
import socket
import sys
import time

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

try:
  # attempt DOMAIN config read
  domains = dict(config.items("DOMAIN"))
except:
  # send warning to logger
  logger.warning("DOMAIN settings not found in config")

u2i_db = idbf_user_to_ip_db(db_host,db_user,db_pass,db_name)

try:
  for line in sys.stdin:
    # check line for eventid
    re_eventid = re.search('.*EventID=\"(\d{4})\".*',line)
    if re_eventid: # eventid found
      # check for eventid 4624 - account successfully logged on
      if re_eventid.group(1) == "4624": # eventid 4624 found, user_add event
        # parse log for mapping info
        # re_event_4624
        #  .group(1) = dc hostname
        #  .group(2) = username
        #  .group(3) = domain
        #  .group(4) = logon type
        #  .group(5) = ip
        #  .group(6) = datetime
        re_event_4624 = re.search('\ (.*?)\ Microsoft.*TargetUserName=\"(.*?)\".*TargetDomainName=\"(.*?)\".*LogonType=\"(\d{1,2})\".*IpAddress=\".*?(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})\".*EventReceivedTime=\"(.*?)\" ',line)
        if re_event_4624: # mapping info found
          # check logon types
          # 2  = interactive       - used
          # 3  = network           - not used
          # 4  = batch             - not used
          # 5  = service           - not used
          # 7  = unlock            - used
          # 8  = networkcleartext  - not used
          # 9  = newcredentials    - not used
          # 10 = remoteinteractive - used
          # 11 = cachedinteractive - used
          if (re_event_4624.group(4) == "2") or (re_event_4624.group(4) == "7") or (re_event_4624.group(4) == "10") or (re_event_4624.group(4) == "11"):
            # try to add or update mapping
            u2i_db.u2i_user_add(time.strftime(re_event_4624.group(6)),adf_user(re_event_4624.group(2)),adf_domain(re_event_4624.group(3),domains),re_event_4624.group(5),("windc (4624) "+re_event_4624.group(1)))
      # check for eventid 4768 - kerberos authentication ticket (tgt) requested
      elif re_eventid.group(1) == "4768":
        # only act on successful events by checking for Status="0x0"
        if "Status=\"0x0\"" in line: # Status="0x0" found
          # parse log for mapping info
          # re_event_4768
          #  .group(1) = dc hostname
          #  .group(2) = username
          #  .group(3) = domain
          #  .group(4) = ip
          #  .group(5) = datetime
          re_event_4768 = re.search('\ (.*?)\ Microsoft.*TargetUserName=\"(.*?)\".*TargetDomainName=\"(.*?)\".*IpAddress=\".*?(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})\".*EventReceivedTime=\"(.*?)\" ',line)
          if re_event_4768: # mapping info found
            # check that username is not a $hostname entry
            if "$" not in  re_event_4768.group(2): # real username found
              # try to add or update mapping
              u2i_db.u2i_user_add(time.strftime(re_event_4768.group(5)),adf_user(re_event_4768.group(2)),adf_domain(re_event_4768.group(3),domains),re_event_4768.group(4),("windc (4768) "+re_event_4768.group(1)))
      # check for eventid 4769 - kerberos service ticket was requested
      elif re_eventid.group(1) == "4769":
        # only act on successful events by checking for Status="0x0"
        if "Status=\"0x0\"" in line: # Status="0x0" found
          # parse log for mapping info
          # re_event_4769
          #  .group(1) = dc hostname
          #  .group(2) = username
          #  .group(3) = domain
          #  .group(4) = ip
          #  .group(5) = datetime
          re_event_4769 = re.search('\ (.*?)\ Microsoft.*TargetUserName=\"(.*?)\".*TargetDomainName=\"(.*?)\".*IpAddress=\".*?(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})\".*EventReceivedTime=\"(.*?)\" ',line)
          if re_event_4769: # mapping info found
            # check that username is not $hostname entry
            if "$" not in  re_event_4769.group(2): # real username found
              # try to add or update mapping
              u2i_db.u2i_user_add(time.strftime(re_event_4769.group(5)),adf_user(re_event_4769.group(2)),adf_domain(re_event_4769.group(3),domains),re_event_4769.group(4),("windc (4769) "+re_event_4769.group(1)))
      # check for eventid 4770 - kerberos service ticket renewed
      elif re_eventid.group(1) == "4770":
        # parse log for mapping info
        # re_event_4770
        #  .group(1) = dc hostname
        #  .group(2) = username
        #  .group(3) = domain
        #  .group(4) = ip
        #  .group(5) = datetime
        re_event_4770 = re.search('\ (.*?)\ Microsoft.*TargetUserName=\"(.*?)\".*TargetDomainName=\"(.*?)\".*IpAddress=\".*?(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})\".*EventReceivedTime=\"(.*?)\" ',line)
        if re_event_4770: # mapping info found
          # check that username is not $hostname entry
          if "$" not in  re_event_4770.group(2): # real username found
            # try to add or update mapping
            u2i_db.u2i_user_add(time.strftime(re_event_4770.group(5)),adf_user(re_event_4770.group(2)),adf_domain(re_event_4770.group(3),domains),re_event_4770.group(4),("windc (4770) "+re_event_4770.group(1)))
      # check for eventid 4776 - domain controller attempted to validate credentials for an account
      elif re_eventid.group(1) == "4776":
        # only act on successful events by checking for Status="0x0"
        if "Status=\"0x0\"" in line: # Status="0x0" found
          # parse log for mapping info
          # re_event_4776
          #  .group(1) = dc hostname
          #  .group(2) = username
          #  .group(3) = workstation
          #  .group(4) = datetime
          re_event_4776 = re.search('\ (.*?)\ Microsoft.*TargetUserName=\"(.*?)\".*Workstation=\"(.*?)\".*EventReceivedTime=\"(.*?)\"',line)
          if re_event_4776: # mapping info found
            # attempt to get ip from workstation dns name
            try:
              ip = socket.gethostbyname(re_event_4776.group(3))
              u2i_db.u2i_user_update(re_event_4776.group(4), re_event_4776.group(2), '', ip, ("windc (4776) "+re_event_4776.group(1)), False, False)
            except:
              logger.info("unable to resolve ip for %s" % re_event_4776.group(3))
      else:
        logger.error("no suitable eventid found in log")
    else:
      logger.error("invalid log")
    
except Exception as err:
  # send error to logger
  logger.error(err)
  exit(0)



