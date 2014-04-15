__author__ = 'Blayne Campbell'
__date__ = '3/25/14'

##################################################
# Fabric script for adding multiple users to
# a list of servers while maintaining unique
# passwords for individual users.
#
# Usage:
#   $ fab <addusr|delusr>
#
# Warning: Do not run as parallel as passwords
#     are only generated once on first pass to
#     remain persistant for the remaining servers.
#
# Dependancies:
#     - fabric api
#     - makepasswd utility
#
##################################################

from fabric.api import *
from crypt import crypt
import subprocess

# Server List
env.hosts = ['server1', 'server2']

# User List ['Full Name', 'UserID']
users = [['First Last1', 'username1'],
        ['First Last2', 'username2'],
        ['First Last3', 'username3'],
        ['First Last4', 'username4'],
        ['First Last5', 'username5']]

# Group List (Comma Seperate for multiple groups ie: group1,group2,group3)
group = 'groupname'


def generatepw():
    """Generate Passwords for users
    """
    allowchar = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*'
    while True:
        usrpw = subprocess.Popen(['makepasswd', '-l 8', '-c %s' % allowchar],
                                 stdout=subprocess.PIPE).stdout.read()
        if not " " in usrpw:  # Ensure no spaces in generated password.
            return usrpw


def addusr():
    for i in users:
        if len(i) == 2:
            pw = generatepw()
            i.append(pw)
        sudo("adduser -c \"%s\" -m -G %s %s" % (i[0], group, i[1]))
        crypted_password = crypt(i[2], 'salt')
        sudo('usermod --password %s %s' % (crypted_password, i[1]), pty=False)
        sudo("chage -d 0 %s" % i[1])
    print "\nUsers for %s\n" % env.host
    for i in users:  # Print the list of Users with credentials
        print "%s" % i[0]
        print "User: %s\nPassword: %s" % (i[1], i[2])


def delusr():
    for i in users:
        run("sudo userdel -r %s" % i[1])
