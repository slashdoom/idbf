###########################################################################
#
# Identity Database Framework (iDbF)
#
# FILENAME:    idbf_user_to_ip_db.py
# DESCRIPTION: database functions for iDbF
#              u2i_user_check
#              u2i_user_add
#              u2i_user_del
#              u2i_user_update
#              u2i_user_scrub
# 
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

import logging
import socket
import mysql.connector
from mysql.connector import errorcode

class pfsidb_user_to_ip_db:

  # class init
  def __init__(self, db_host, db_user, db_pass, db_name):

    #setup logging
    self.logger = logging.getLogger()
    self.logger.setLevel(logging.DEBUG)
    #setup file logging handler
    fh = logging.FileHandler("{0}.log".format(__name__))
    fh.setLevel(logging.WARNING)
    fh_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)-8s - %(message)s")
    fh.setFormatter(fh_format)
    self.logger.addHandler(fh)
    # setup syslog logging handler
    # hostname = socket.gethostname()
    # sh = logging.SysLogHandler(address=('localhost', 20514))
    # sh.setLevel(logging.INFO)
    # sh_format = logging.Formatter("%(asctime)s %(hostname)s %(self.app_name)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
    # sh.setFormatter(sh_format)
    # self.logger.addHandler(sh)

    # connect to mysql server
    try:
      self.db_conn = mysql.connector.connect(host=db_host,
                                             user=db_user,
                                             password=db_pass,
                                             database=db_name,
                                             buffered=True)
    # check mysql connection
    except mysql.connector.Error as err: # mysql connection error
      self.logger.error('MySQL error: %s', err)
      exit(0)

    # mysql connection successful, create cursor
    self.logger.debug("MySQL connected to %s" % db_name)
    self.db_cur = self.db_conn.cursor()

  # check database for existing ip address record
  def u2i_user_check(self, ip):
    # query user_to_ip table by IP address
    sql_query = ("SELECT * FROM user_to_ip WHERE ip='%s'" % ip)
    self.db_cur.execute(sql_query)
    # include column names in results
    sql_columns = self.db_cur.description
    sql_results = [{sql_columns[index][0]:column for index, column in enumerate(value)} for value in self.db_cur.fetchall()]
    # check for results returned
    if self.db_cur.rowcount > 0: # results found
      # debug log
      self.logger.debug("u2i_user_check() found match for %s" % ip)
      # return check results
      return sql_results[0]
    else: # no results found
      # debug log
      self.logger.debug("u2i_user_check() found no match for %s" % ip)
      # return negative results
      return False

  # add or update database with new ip mapping
  def u2i_user_add(self, datetime, user, domain, ip, source):
    # check to matching ip address in database
    if self.u2i_user_check(ip) == False: # ip address doesn't exist
      # create new record
      sql_query = ( "INSERT INTO user_to_ip (datetime, user, domain, ip, source) "
                    "VALUES (%s, %s, %s, %s, %s)" )
      insert_data = (datetime, user.lower(), domain.lower(), ip, source)
      self.db_cur.execute(sql_query, insert_data)
      self.db_conn.commit()
      # debug log
      self.logger.debug("u2i_user_add() added new user to ip mapping %s - %s" % (user.lower(), ip))
    else: # ip address already exists
      # attempt record update
      self.logger.debug("u2i_user_add() existing record for for %s.  attempting update..." % (ip))
      self.u2i_user_update(datetime, user, domain, ip, source, True, True)

  # delete user to ip mapping from database
  def u2i_user_del(self, ip):
    # check that record to be deleted exists
    if self.u2i_user_check(ip): # ip address exists
      # delete user_to_ip row by ip address
      sql_query = ("DELETE FROM user_to_ip WHERE ip = %s")
      self.db_cur.execute(sql_query, (ip,))
      self.db_conn.commit()
      # create record deleted log
      self.logger.debug("u2i_user_del() deleted record for %s" % (ip))
      return True
    else: # no matching ip found
      # log ip not found error
      self.logger.error("u2i_user_del() called but ip %s not found" % ip)
      return False

  # update existing user to ip mapping record
  def u2i_user_update(self, datetime, user, domain, ip, source, overwrite=False, domain_req=False):
    # check that record to be updated exists
    existing_record = self.u2i_user_check(ip)
    if existing_record == False: # no matching ip found
      self.logger.error("u2i_user_update() called but no matching ip found for %s" % ip)
      return False
    else: # ip found
      if domain_req:
        # confirm that user and domain match, record to be updated
        if (existing_record["user"] == user.lower()) and (existing_record["domain"] == domain.lower()): # user and domain match
          # update user_to_ip record
          sql_query = ( "UPDATE user_to_ip "
                        "SET datetime=%s, source=%s WHERE ip=%s" )
          update_data = (datetime, source, ip)
          self.db_cur.execute(sql_query, update_data)
          self.db_conn.commit()
          # create record update log
          self.logger.debug("u2i_user_update() record updated for %s@%s - %s" % (user.lower(), domain.lower(), ip))
          return True
        else: # user and domain mismatch
          # check if overwrite is specified
          if overwrite: # overwrite mismatched record
            # delete old ip record
            self.u2i_user_del(ip)
            # add new record
            sql_query = ( "INSERT INTO user_to_ip (datetime, user, domain, ip, source) "
                          "VALUES (%s, %s, %s, %s, %s)" )
            insert_data = (datetime, user.lower(), domain.lower(), ip, source)
            self.db_cur.execute(sql_query, insert_data)
            self.db_conn.commit()
            self.logger.debug("u2i_user_update() replaced ip mapping for %s" % (ip))
            return True
          else: # leave existing record
            self.logger.info("u2i_user_update() %s not updated.  domain and user mismatch" % (ip))
            return False
      else:
        # confirm that user matches, record to be updated
        if existing_record["user"] == user.lower(): # user match
          # update user_to_ip record
          sql_query = ( "UPDATE user_to_ip "
                        "SET datetime=%s, source=%s WHERE ip=%s" )
          update_data = (datetime, source, ip)
          self.db_cur.execute(sql_query, update_data)
          self.db_conn.commit()
          # create record update log
          self.logger.debug("u2i_user_update() record updated for %s - %s" % (user.lower(), ip))
          return True
        else: # user mismatch
          # check if overwrite is specified
          if overwrite: # overwrite mismatched record
            # delete old ip record
            self.u2i_user_del(ip)
            # add new record
            sql_query = ( "INSERT INTO user_to_ip (datetime, user, domain, ip, source) "
                          "VALUES (%s, %s, %s, %s, %s)" )
            insert_data = (datetime, user.lower(), domain.lower(), ip, source)
            self.db_cur.execute(sql_query, insert_data)
            self.db_conn.commit()
            self.logger.debug("u2i_user_update() replaced ip mapping for %s" % (ip))
            return True
          else: # leave existing record
            self.logger.info("u2i_user_update() %s not updated.  user mismatch" % (ip))
            return False

# scrub/delete records older than specified time
  def u2i_user_scrub(self, day, hour, minute):
    # query user_to_ip table by datetime
    sql_query = ("select * from user_to_ip WHERE datetime < (NOW() - INTERVAL %s MINUTE - INTERVAL %s HOUR - INTERVAL %s DAY)")
    self.db_cur.execute(sql_query, (minute, hour, day,))
    # check for results returned
    if self.db_cur.rowcount > 0: # results found
      # include column names in results
      sql_columns = self.db_cur.description
      sql_results = [{sql_columns[index][0]:column for index, column in enumerate(value)} for value in self.db_cur.fetchall()]
      # scrub records
      for row in sql_results:
        # call delete for ip in result row
        self.u2i_user_del(row["ip"])
        # log user deleted
        self.logger.info("u2i_user_scrub() deleted %s\\%s - %s" % (row["user"], row["domain"], row["ip"]))
      # return check results
      return True
    else: # no results found
      # debug log
      self.logger.debug("u2i_user_scrub() no records met scrub criteria")
      # return negative results
      return False

  # class delete
  def __del__(self):
    self.db_conn.close()
