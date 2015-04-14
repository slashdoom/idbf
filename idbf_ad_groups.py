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
import re

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
  # split domain by '.' and add dc= to each domain part
  for part in (domain.split(".")):
    domain_dc_parts.append("dc=%s" % (part))
    # rejoin the domain parts with dc=part
  ldap_domain = (','.join(domain_dc_parts))
  print (ldap_domain)

  # query ldap for all groups
  ldap_group_list = c.extend.standard.paged_search( search_base   = ldap_domain,
                                                    search_filter = "(&(objectcategory=group))",
                                                    search_scope  = ldap3.SUBTREE,
                                                    attributes    = ["primaryGroupToken","cn"],
                                                    paged_size    = 5,
                                                    generator     = True)
  # query ldap for all users
  ldap_user_list = c.extend.standard.paged_search( search_base   = ldap_domain,
                                                   search_filter = "(&(objectCategory=person)(objectClass=user))",
                                                   search_scope  = ldap3.SUBTREE,
                                                   attributes    = ["sAMAccountName","memberOf","primaryGroupID"],
                                                   paged_size    = 5,
                                                   generator     = True)

  #for ldap_group in ldap_group_list:
   # print (ldap_group["attributes"]["primaryGroupToken"])
  ldap_user_count = 0
  # process each user to build group list
  for ldap_user in ldap_user_list:
    ldap_user_count += 1
    # extract sAMAccountName from ldap query
    ldap_user_samaccountname = (ldap_user["attributes"]["sAMAccountName"][0].lower())
    # extract memberOf list from ldap query
    ldap_user_memberof_list = ldap_user.get("attributes").get("memberOf")
    # extract primaryGroupID from ldap query
    ldap_user_primarygroupid = (ldap_user["attributes"]["primaryGroupID"][0])

    # convert memberOf list to usable format
    ldap_user_memberof_list_regular = []
    if ldap_user_memberof_list is not None:
      for group in ldap_user_memberof_list:
        re_group = re.search('CN=(.*?),',group)
        ldap_user_memberof_list_regular.append(re_group.group(1))
      ldap_user_memberof = (",".join(ldap_user_memberof_list_regular))
    else:
      ldap_user_memberof = ""

    # add primary group to list
    for ldap_group in ldap_group_list:
      if ldap_group["attributes"]["primaryGroupToken"][0] == ldap_user_primarygroupid:
        print (ldap_group["attributes"]["cn"][0])
        break

    #print ("%s: %s" % (ldap_user_samaccountname, ldap_user_memberof))

    #print (c.search(ldap_domain,("(member:1.2.840.113556.1.4.1941:cn=%s,cn=Users,%s)" % (ldap_samaccountname, ldap_domain)),ldap3.SUBTREE,attributes=["cn"]))

  print (ldap_user_count)