# !/usr/bin/env python
__author__ = 'Blayne Campbell'
__date__ = '3/25/14'

##################################################
# Fabric script for adding multiple users to a list of hosts. This script
# also allows the administrator to set the same unique password for each user
# across all hosts if desired. (see addusr params for persistant passwords)
#
# All new accounts are expired by default and will force each user to reset
# their password upon first login. Users have approximatly 30 days to login
# and change their temporary password or the account will turn inactive.
#
# Usage:
#   $ fab -l will list commands
#   $ fab -d <command> will provide command info & params
#
# Warning:
# Do not run as parallel as passwords are only generated once for initial
# host to allow persistant temporary password for all hosts being processed.
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


# Target hosts
env.hosts = ['server1', 'server2']

# User List ['Full Name', 'UserID']
users = [['First Last1', 'Comment', 'username1'],
         ['First Last2', 'Comment', 'username2'],
         ['First Last3', 'Comment', 'username3'],
         ['First Last4', 'Comment', 'username4'],
         ['First Last5', 'Comment', 'username5']]

# Group List (Comma Seperate for multiple groups ie: group1,group2,group3)
group = 'groupname'


def generatepw():
    """ Generates a random password that meets the following Password criteria:
        13 characters length
        4 letters in uppercase
        3 special character (!@#$&*)
        3 numerals (0-9)
        3 letters in lowercase
    :return: Random password that meets criteria
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
def addusr(pp=None):
    """ Adds Users specified by 'users' & creates group
    :param pp: Set True if password should be the same on all hosts
    :return: Nothing

    Usage:
        Different password for each hosts:
        $ fab addusr
        Persistant passwords across all hosts
        $ fab addusr:pp=True
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
        if len(i) == 3:
            pw = generatepw()
            i.append(pw)
        with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
            sudo("adduser -c \"%s - %s\" -m -G %s %s"
                 % (i[0], i[1], group, i[2]))
            crypted_password = crypt.crypt(i[3],
                                           crypt.mksalt(crypt.METHOD_CRYPT))
            sudo('usermod --password %s %s' % (crypted_password,
                                               i[2]), pty=True)
            # Modify the following rules to your needs: (Read chage manpage)
            sudo("chage -E -1 -W 11 -m 7 -M 42 -I 30 -d now-44days %s" % i[2])
    print("\nUsers for %s\n" % env.host)
    for i in users:  # Print the list of Users with credentials
        print("%s" % i[0])
        print("User: %s\nPassword: %s" % (i[1], i[3]))
    if not pp:
        for i in users:
            if len(i) == 4:
                i.pop()


@task
def delusr():
    """ Removes users specified by 'users' & leaves group intact
    :return: Nothing
    """
    for i in users:
        sudo("userdel -r %s" % i[2])
