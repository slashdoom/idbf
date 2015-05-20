###########################################################################
#
# Identity Database Framework (idbf)
#
# FILENAME:    idbf_acl_builder.py
# DESCRIPTION: flask based web app to return ip addresses of users or
#              groups
#
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

from flask import Flask
from flask import request
import configparser
import logging
import mysql.connector
import os

# open config file
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "..", "etc", "idbf_conf"))

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

# create flask application
app = Flask(__name__)

# decoration for user ip list builder
@app.route('/user', methods=['GET', 'POST'])
def user_to_ip():
  # get username and domain from post arguments
  user   = request.args.get("user")
  domain = request.args.get("domain")
  try:
    # connect to mysql server
    db_conn = mysql.connector.connect(host=db_host,
                                      user=db_user,
                                      password=db_pass,
                                      database=db_name,
                                      buffered=True)
    # mysql connection successful, create cursor
    logger.debug("idbf_acl_builder MySQL connected to %s" % db_name)
    db_cur = db_conn.cursor()
    # query idb_view view by domain and user
    sql_query = ("SELECT ip FROM idb_view WHERE user=%s AND domain=%s")
    db_cur.execute(sql_query, (user,domain,))
    ip_list = ""
    # build ip list from results
    for (ip) in db_cur:
      ip_list += (ip[0]+"\n")
    # close out sql connector
    db_cur.close()
    db_conn.close()
    return ip_list
  # on error return no ip addresses
  except:
    return ""

# decoration for user ip list builder
@app.route('/group', methods=['GET', 'POST'])
def group_to_ip():
  group  = request.args.get("group")
  domain = request.args.get("domain")
  try:
    # connect to mysql server
    db_conn = mysql.connector.connect(host=db_host,
                                      user=db_user,
                                      password=db_pass,
                                      database=db_name,
                                      buffered=True)
    # mysql connection successful, create cursor
    logger.debug("idbf_acl_builder MySQL connected to %s" % db_name)
    db_cur = db_conn.cursor()
    # query idb_view view by domain and group
    sql_query = ("SELECT v_ip FROM idb_view WHERE v_groups LIKE '%|{}|%'").format(domain+"\\\\\\\\"+group)
    db_cur.execute(sql_query)
    # build ip list from results
    ip_list = ""
    for (ip) in db_cur:
      ip_list += (ip[0]+"\n")
    # close out sql connector
    db_cur.close()
    db_conn.close()
    # return ip list to web page
    return ip_list
  # on error return no ip addresses
  except:
    return ""

# catch all to return blank page for other urls
@app.route('/', defaults={'path': ''})
@app.route('/<path>')
def catch_all(path):
  return ""

# return blank page for 404s
@app.errorhandler(404)
def page_not_found(error):
  return ""

# run main flask web application
if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)
