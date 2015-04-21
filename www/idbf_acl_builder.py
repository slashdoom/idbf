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
from flask import jsonify
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
  db_host = config["DATABASE"]["db_host"]
  db_user = config["DATABASE"]["db_user"]
  db_pass = config["DATABASE"]["db_pass"]
  db_name = config["DATABASE"]["db_name"]
except:
  # send error to logger
  logger.error("DATABASE connection settings not found in config")
  exit(0)

# connect to mysql server
try:
  db_conn = mysql.connector.connect(host=db_host,
                                    user=db_user,
                                    password=db_pass,
                                    database=db_name,
                                    buffered=True)
  # mysql connection successful, create cursor
  logger.debug("idbf_user_groups_db MySQL connected to %s" % db_name)
  db_cur = db_conn.cursor()
# check mysql connection
except mysql.connector.Error as err: # mysql connection error
  logger.error('idbf_user_groups_db MySQL error: %s', err)
  exit(0)

# create flask application
app = Flask(__name__)

# decoration for user ip list builder
@app.route('/user/<user>')
def user_to_ip(user):
  try:
    # query idb_view view by user
    sql_query = ("SELECT ip FROM idb_view WHERE user=%s")
    db_cur.execute(sql_query, (user,))
    if db_cur.rowcount > 0: # results found
      print (db_cur.fetchall())
      for (user_ip) in db_cur.fetchall():
        user_ip_list =+ user
      return user_ip_list
    else:
      return ""
  except:
    return ""

# decoration for user ip list builder
@app.route('/group/<group>')
def group_to_ip(group):
  return "group: %s" % group

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