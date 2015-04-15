###########################################################################
#
# Identity Database Framework (iDbF)
#
# FILENAME:    idbf_user_groups_db.py
# DESCRIPTION: user group table database functions for iDbF
#              ug_user_check
#              ug_user_add
#              ug_user_del
#              ug_user_update
#              ug_user_scrub
#
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

import logging
import mysql.connector

class idbf_user_groups_db:

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

    # connect to mysql server
    try:
      self.db_conn = mysql.connector.connect(host=db_host,
                                             user=db_user,
                                             password=db_pass,
                                             database=db_name,
                                             buffered=True)
    # check mysql connection
    except mysql.connector.Error as err: # mysql connection error
      self.logger.error('idbf_user_groups_db MySQL error: %s', err)
      exit(0)

    # mysql connection successful, create cursor
    self.logger.debug("idbf_user_groups_db MySQL connected to %s" % db_name)
    self.db_cur = self.db_conn.cursor()

  # check database for existing user/group mapping
  def ug_user_check(self, user, domain):
    # query user_groups table by user and domain
    sql_query = ("SELECT * FROM user_groups WHERE user=%s AND domain=%s")
    self.db_cur.execute(sql_query, (user, domain))
    # include column names in results
    sql_columns = self.db_cur.description
    sql_results = [{sql_columns[index][0]:column for index, column in enumerate(value)} for value in self.db_cur.fetchall()]
    # check for results returned
    if self.db_cur.rowcount > 0: # results found
      # debug log
      self.logger.debug("ug_user_check() found match for %s@%s" % (user.lower(), domain.lower()))
      # return check results
      return sql_results[0]
    else: # no results found
      # debug log
      self.logger.debug("ug_user_check() found no match for %s@%s" % (user.lower(), domain.lower()))
      # return negative results
      return False

  # add or update database with new user/group mapping
  def ug_user_add(self, datetime, user, domain, groups):
    # check for matching user in database
    if self.ug_user_check(user, domain) == False: # user doesn't exist
      # create new record
      sql_query = ( "INSERT INTO user_groups (datetime, user, domain, groups) "
                    "VALUES (%s, %s, %s, %s)" )
      insert_data = (datetime, user.lower(), domain.lower(), groups.lower(),)
      self.db_cur.execute(sql_query, insert_data)
      self.db_conn.commit()
      # debug log
      self.logger.debug("ug_user_add() added new user to group mapping for %s@%s" % (user.lower(), domain.lower()))
    else: # user already exists
      # attempt record update
      self.logger.debug("ug_user_add() existing record for %s@%s.  attempting update..." % (user.lower(), domain.lower()))
      self.ug_user_update(datetime, user, domain, groups, True)

  # delete user/groups mapping from database
  def ug_user_del(self, user, domain):
    # check that record to be deleted exists
    if self.ug_user_check(user, domain): # user/group mapping exists
      # delete user row by user and domain
      sql_query = ("DELETE FROM user_groups WHERE user=%s AND domain=%s")
      self.db_cur.execute(sql_query, (user, domain,))
      self.db_conn.commit()
      # create record deleted log
      self.logger.debug("ug_user_del() deleted record for %s@%s" % (user.lower(), domain.lower()))
      return True
    else: # no matching user found
      # log ip not found error
      self.logger.error("ug_user_del() called but ip %s@%s not found" % (user.lower(), domain.lower()))
      return False

  # update existing user/group record
  def ug_user_update(self, datetime, user, domain, groups, overwrite=False):
    # check that record to be updated exists
    existing_record = self.ug_user_check(user, domain)
    if existing_record == False: # no matching user found
      self.logger.error("ug_user_update() called but no matching user found for %s@%s" % (user.lower(), domain.lower()))
      return False
    else: # user found
      # check if domain/user and groups match existing record
      if (existing_record["user"] == user.lower()) and (existing_record["domain"] == domain.lower()) and (existing_record["groups"] == groups.lower().replace("//","/")): # record matches
        # update user/group timestamp only
        sql_query = ( "UPDATE user_groups "
                      "SET datetime=%s WHERE user=%s AND domain=%s" )
        update_data = (datetime, user, domain)
        self.db_cur.execute(sql_query, update_data)
        self.db_conn.commit()
        # create record update log
        self.logger.debug("ug_user_update() record updated for %s@%s" % (user.lower(), domain.lower()))
        return True
      else: # user and domain mismatch
        # check if overwrite is specified
        if overwrite: # overwrite mismatched record
          # delete old ip record
          self.ug_user_del(user, domain)
          # add new record
          sql_query = ( "INSERT INTO user_groups (datetime, user, domain, groups) "
                        "VALUES (%s, %s, %s, %s)" )
          insert_data = (datetime, user.lower(), domain.lower(), groups.lower(),)
          self.db_cur.execute(sql_query, insert_data)
          self.db_conn.commit()
          self.logger.debug("ug_user_update() replaced user/group mapping for %s@%s" % (user.lower(), domain.lower()))
          return True
        else: # leave existing record
          self.logger.info("ug_user_update() %s@%s not updated.  user/group mismatch" % (user.lower(), domain.lower()))
          return False

# scrub/delete records older than specified time
  def ug_user_scrub(self, day, hour, minute):
    # query user_groups table by datetime
    sql_query = ("select * from user_groups WHERE datetime < (NOW() - INTERVAL %s MINUTE - INTERVAL %s HOUR - INTERVAL %s DAY)")
    self.db_cur.execute(sql_query, (minute, hour, day,))
    # check for results returned
    if self.db_cur.rowcount > 0: # results found
      # include column names in results
      sql_columns = self.db_cur.description
      sql_results = [{sql_columns[index][0]:column for index, column in enumerate(value)} for value in self.db_cur.fetchall()]
      # scrub records
      for row in sql_results:
        # call delete for user in result row
        self.ug_user_del(row["user"],row["domain"])
        # log user deleted
        self.logger.info("ug_user_scrub() deleted %s@%s" % (row["user"], row["domain"]))
      # return check results
      return True
    else: # no results found
      # debug log
      self.logger.debug("ug_user_scrub() no records met scrub criteria")
      # return negative results
      return False

  # class delete
  def __del__(self):
    self.db_conn.close()