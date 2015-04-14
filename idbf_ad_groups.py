#!/usr/bin/env python
###########################################################################
#
# Identity Database Framework (idbf)
#
# FILENAME:    idbf_ad_groups.py
# DESCRIPTION: Time based scrubber script for iDbF
#
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

import configparser
import ldap3
import logging
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

try:
  # attempt LDAP config read
  ldap_server   = config["LDAP"]["server"]
  ldap_port     = config["LDAP"]["port"]
  ldap_username = config["LDAP"]["username"]
  ldap_password = config["LDAP"]["password"]
except:
  # send warning to logger
  logger.error("LDAP settings not found in config")
  exit(0)

s = ldap3.Server(ldap_server, port=int(ldap_port))
c = ldap3.Connection(s, user = ldap_username, password=ldap_password, auto_bind=True)

# debug connection status
logger.debug(c)

# convert domain to ldap format
for domain in domains:
  domain_dc_parts = []
  for part in (domain.split(".")):
    domain_dc_parts.append("dc=%s" % (part))
  ldap_domain = (','.join(domain_dc_parts))
  print (ldap_domain)
  ldap_entry_list = c.extend.standard.paged_search( search_base   = ldap_domain,
                                                    search_filter = "(&(objectCategory=person)(objectClass=user))",
                                                    search_scope  = ldap3.SUBTREE,
                                                    attributes    = ["sAMAccountName","memberOf"],
                                                    paged_size    = 5,
                                                    generator     = True)

  ldap_entry_count = 0
  for ldap_entry in ldap_entry_list:
    ldap_entry_count += 1
    ldap_samaccountname = (ldap_entry['attributes']['sAMAccountName'][0].lower())
    #ldap_memberof = (ldap_entry['attributes']['memberOf'])
    ldap_memberof = ldap_entry.get('attributes').get('memberOf')

    print ("%s: %s" % (ldap_samaccountname, ldap_memberof))

    #print (c.search(ldap_domain,("(member:1.2.840.113556.1.4.1941:cn=%s,cn=Users,%s)" % (ldap_samaccountname, ldap_domain)),ldap3.SUBTREE,attributes=["cn"]))

  print (ldap_entry_count)