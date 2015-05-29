#!/usr/bin/env python3
###########################################################################
#
# Identity Database Framework (idbf)
#
# FILENAME:    idbf_ufdb_execuser.py
# DESCRIPTION: script to provide ufdbguard with usernames through
#              execuserlist
#
# AUTHOR:      Patrick K. Ryon (slashdoom)
# LICENSE:     3 clause BSD (see LICENSE file)
#
###########################################################################

import getopt
import sys

def main(argv):
   group = ''
   user = ''
   try:
      opts, args = getopt.getopt(argv,"g:u:",["group=","user="])
   except getopt.GetoptError:
      print('idbf_ufdb_execuser.py -g <group> or -u <username>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('idbf_ufdb_execuser.py -g <group> or -u <username>')
         sys.exit()
      elif opt in ("-g", "--group"):
         group = arg
      elif opt in ("-u", "--user"):
         user = arg
   print('Group is: ', group)
   print('User is: ', user)

if __name__ == "__main__":
   main(sys.argv[1:])