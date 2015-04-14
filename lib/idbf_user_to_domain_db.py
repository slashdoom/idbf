###########################################################################
#
# Identity Database Framework (iDbF)
#
# FILENAME:    idbf_user_to_domain_db.py
# DESCRIPTION: user to domain table database functions for iDbF
#              u2d_user_check
#              u2d_user_add
#              u2d_user_del
#              u2d_user_update
#              u2d_user_scrub
#
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

import logging
import mysql.connector

class pfsidb_user_to_domain_db:

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
      self.logger.error('MySQL error: %s', err)
      exit(0)

    # mysql connection successful, create cursor
    self.logger.debug("MySQL connected to %s" % db_name)
    self.db_cur = self.db_conn.cursor()

  # check database for existing username
  def u2d_user_check(self, user, domain):
    # query user_to_ip table by IP address
    sql_query = ("SELECT * FROM user_to_domain WHERE user='%s'" % user)
    self.db_cur.execute(sql_query)
    # include column names in results
    sql_columns = self.db_cur.description
    sql_results = [{sql_columns[index][0]:column for index, column in enumerate(value)} for value in self.db_cur.fetchall()]
    # check for results returned
    if self.db_cur.rowcount > 0: # results found
      # debug log
      self.logger.debug("u2d_user_check() found match for %s" % ip)
      # return check results
      return sql_results[0]
    else: # no results found
      # debug log
      self.logger.debug("u2d_user_check() found no match for %s" % ip)
      # return negative results
      return False

  # add or update database with new user/group mapping
  def u2d_user_add(self, datetime, user, domain, groups):
    # check for matching user in database
    if self.u2i_user_check(user, domain) == False: # user doesn't exist
      # create new record
      sql_query = ( "INSERT INTO user_to_domain (datetime, user, domain, groups) "
                    "VALUES (%s, %s, %s, %s)" )
      insert_data = (datetime, user.lower(), domain.lower(), groups)
      self.db_cur.execute(sql_query, insert_data)
      self.db_conn.commit()
      # debug log
      self.logger.debug("u2d_user_add() added new user to group mapping for %s" % (user.lower()))
    else: # user already exists
      # attempt record update
      self.logger.debug("u2d_user_add() existing record for %s.  attempting update..." % (user.lower()))
      self.u2i_user_update(datetime, user, domain, groups, True)