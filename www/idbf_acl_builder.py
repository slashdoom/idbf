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

# create flask application
app = Flask(__name__)

# decoration for user ip list builder
@app.route('/user/<user>')
def user_to_ip(user):
  return "user: %s" % user

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