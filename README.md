# iDbF (Identity Database Framework)
iDbF is a collection of scripts to create an identity (user/ip/group mapping) database for use with pfSense, Squid snd other applications for the sake of achieving "Next Generation" firewall like features.

# Requirements:
 * Python3
 * MySQL Python Connector
 * MySQL/MariaDB

For Windows DC mappings:
 * Syslog-NG on iDbF server
 * NXLog on Windows DC's

For pfSense URL Table Aliases
 * Flask
 * Webserver (NGINX, Apache2, etc.)
 * WSGI/uWSGI

For URL Filtering
 * Squid 3.4
 * ufdbGuard 1.31
