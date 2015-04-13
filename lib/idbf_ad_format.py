
###########################################################################
#
# Identity Database Framework (iDbF)
#
# FILENAME:    idbf_ad_format.py
# DESCRIPTION: AD formatting functions for iDbF
#              adf_user
#              adf_domain
#
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

import logging
import re

#setup logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# setup file logging handler
fh = logging.FileHandler("{0}.log".format(__name__))
fh.setLevel(logging.WARNING)
fh_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')
fh.setFormatter(fh_format)
logger.addHandler(fh)

# standardize usernames from AD logs
def adf_user(username):
  # check if user is in 'username' or 'username@domain' format
  if "@" in username: # 'username@domain' format found
    # convert to 'username' format
    re_username = re.search('(.*?)@',username)
    logger.debug("adf_user() %s converted to %s" % (username, re_username.group(1)))
    return re_username.group(1)
  else: # 'username' format found
    logger.debug("adf_user() username %s maintained" % (username))
    return username.lower()

# standardize domains from AD logs
def adf_domain(domain, domain_list):
  # check if domain is in 'domain' or 'domain.suffix' format
  if "." not in domain: # 'domain' format found
    # convert to 'domain.suffix' format
    f_domain = ([k for k, v in domain_list.items() if v == domain.lower()][0])
    logger.debug("adf_domain() %s converted to %s" % (domain, f_domain))
    return f_domain.lower()
  else: # domain.suffix format found
    logger.debug("adf_domain() domain %s maintained" % (domain))
    return domain.lower()
