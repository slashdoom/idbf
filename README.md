# iDbF (Identity Database Framework)
iDbF is a collection of scripts to create an identity (user/ip/group mapping) database for use with pfSense, Squid snd other programs for the sake of achieve "Next Generation" firewall like features.

# Requires:
 * Python3
 * MySQL Python Connector
 * MySQL/MariaDB

For Windows DC mappings:
 * Syslog-NG on iDbF server
 * NXLog on Windows DC's

For pfSense URL Table Aliases
 * Flask
 * WSGI/UWSGI
 * Webserver (NGINX, Apache2, etc.)
