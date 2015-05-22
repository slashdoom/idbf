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
      opts, args = getopt.getopt(argv,"hg:u:",["a_group=","a_user="])
   except getopt.GetoptError:
      print 'test.py -g <inputfile> or -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputfile> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   print 'Input file is "', inputfile
   print 'Output file is "', outputfile

if __name__ == "__main__":
   main(sys.argv[1:])