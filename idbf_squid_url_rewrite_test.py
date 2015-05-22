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


import logging
import re
import sys

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

try:
  for line in sys.stdin:
    logger.debug(line)
    print("OK")

except Exception as err:
  # send error to logger
  logger.error(err)
  exit(0)