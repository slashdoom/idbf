#!/usr/bin/env python3
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
import itertools
import ldap3
import logging
import os
import re
import time

from lib.idbf_user_groups_db import *

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

ug_db = idbf_user_groups_db(db_host,db_user,db_pass,db_name)

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
  for domain_part in (domain.split(".")):
    domain_dc_parts.append("dc=%s" % (domain_part))
  # rejoin the domain parts with dc=part
  ldap_domain = (','.join(domain_dc_parts))

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

  # process each user to build group list
  for ldap_user in ldap_user_list:
    # extract sAMAccountName from ldap query
    ldap_user_samaccountname = (ldap_user["attributes"]["sAMAccountName"][0].lower())
    # extract memberOf list from ldap query
    ldap_user_memberof_list = ldap_user.get("attributes").get("memberOf")
    # extract primaryGroupID from ldap query
    ldap_user_primarygroupid = (ldap_user["attributes"]["primaryGroupID"][0])

    # check that user has groups
    group_list = []
    if ldap_user_memberof_list is not None: # groups found
      # reformat group from ldap format to domain\group
      for group in ldap_user_memberof_list:
        # separate ldap group name from ldap domain
        re_group = re.search('cn=(.*?),.*?dc=(.*)',group.lower())
        group_name = re_group.group(1)
        group_domain = re_group.group(2)
        # convert ldap domain to fqdn domain
        group_domain = group_domain.replace(",dc=",".")
        # add domain\group to list
        group_list.append("%s\\%s" % (group_domain, group_name))

    # clone/tee domain group to process
    ldap_group_list, gen_ldap_group_list = itertools.tee(ldap_group_list)
    # add primary group to list
    for ldap_group in gen_ldap_group_list:
      # attempt to match user primarygroupid to group primarygrouptoken
      if ldap_group["attributes"]["primaryGroupToken"][0] == ldap_user_primarygroupid: # match found
        # add primary domain\group to list
        group_list.append("%s\\%s" % (domain, ldap_group["attributes"]["cn"][0]))
        # exit loop once match found
        break

    # convert domain\group list to pipe separated string
    ldap_user_memberof = "|".join(sorted(group_list))
    ldap_user_memberof = "|" + ldap_user_memberof + "|"

    # add user and groups to database
    ug_db.ug_user_add(time.strftime('%Y-%m-%d %H:%M:%S'), ldap_user_samaccountname, domain, ldap_user_memberof)