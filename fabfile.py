# !/usr/bin/python
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
# Warning:
#  Do not run as parallel task because passwords
#  are only generated once on first pass to
#  remain persistant for the remaining servers.
#
# Dependancies:
#     - fabric api
#     - makepasswd utility
#
##################################################

import subprocess
import crypt
import re

from fabric.api import *


# Target Servers
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
    """ Generates a random password that meets
    Password Criteria:
        13 characters length
        4 letters in Upper Case
        3 Special Character (!@#$&*)
        3 numerals (0-9)
        3 letters in Lower Case
    :return: Random Password that meets criteria
    """
    # Only allow visual friendly characters to minimize user frustration
    allowchar = 'abcdefghijkmnpqrstuvwxyz' \
                'ABCDEFGHIJKLMNPQRSTUVWXYZ23456789!@#$&*'
    while True:
        usrpw = subprocess.Popen(['makepasswd', '-l 13', '-c %s' % allowchar],
                                 stdout=subprocess.PIPE).stdout.read()
        strongpw = re.compile(r'^(?=.*[A-Z].*[A-Z].*[A-Z].*[A-Z])'
                              r'(?=.*[!@#$&*].*[!@#$&*].*[!@#$&*])'
                              r'(?=.*[0-9].*[0-9].*[0-9])'
                              r'(?=.*[a-z].*[a-z].*[a-z])'
                              r'.{13}$')
        if strongpw.match(usrpw):
            return usrpw


@task
def addusr():
    """ Adds Users specified by 'users' & creates group
    :return: Nothing
    """
    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        addgroup = sudo("groupadd %s" % group)
        if addgroup.return_code == 0:
            print("Group added %s: " % group)
        elif addgroup.return_code == 9:
            print("Group already exists: %s" % group)
        else:
            print("An error occured while adding group: %s" % group)
    for i in users:
        if len(i) == 2:
            pw = generatepw()
            i.append(pw)
        with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
            sudo("adduser -c \"%s\" -m -G %s %s" % (i[0], group, i[1]))
            crypted_password = crypt.crypt(i[2],
                                           crypt.mksalt(crypt.METHOD_CRYPT))
            sudo('usermod --password %s %s' % (crypted_password,
                                               i[1]), pty=True)
            # Modify the following rules to your needs: (Read chage manpage)
            sudo("chage -E -1 -W 11 -m 7 -M 42 -I 30 %s" % i[1])
    print("\nUsers for %s\n" % env.host)
    for i in users:  # Print the list of Users with credentials
        print("%s" % i[0])
        print("User: %s\nPassword: %s" % (i[1], i[2]))


@task
def delusr():
    """ Removes users specified by 'users' & leaves group intact
    :return: Nothing
    """
    for i in users:
        sudo("userdel -r %s" % i[1])
