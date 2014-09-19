# !/usr/bin/env python
#############################################################
# fabric-adduser
# ==============
#
# Fabric script for adding multiple users to a list of hosts
#############################################################
__author__ = 'Blayne Campbell'
__date__ = '3/25/14'

import random
import string
import crypt
import sys
import os
import re

from fabric.api import *

# Password Complexity Settings
uppercase = 4
lowercase = 3
numerals = 3
special = 3

# Target hosts
env.hosts = ['server1', 'server2']

# User List ['Full Name', 'UserID']
users = [['First Last1', 'Comment', 'username1'],
         ['First Last2', 'Comment', 'username2'],
         ['First Last3', 'Comment', 'username3'],
         ['First Last4', 'Comment', 'username4'],
         ['First Last5', 'Comment', 'username5']]

# Group List (Comma Separated for multiple groups ie: group1,group2,group3)
groups = 'group1,group2'


def generatepw():
    """ Generates a random password that meets the password criteria outlined
    in the settings file:
    :return: Random password that meets criteria
    """
    # Only allow visual friendly characters to minimize user frustration
    allchars = string.ascii_letters + string.digits + '.!@#$%^&*'
    allowchar = re.sub('[oOIl0]', '', allchars)
    uppers = '.*[A-Z]' * uppercase
    lowers = '.*[a-z]' * lowercase
    numers = '.*[0-9]' * numerals
    spchar = '.*[!@#$&*]' * special
    pwlength = (uppercase + lowercase + numerals + special)
    random.seed = (os.urandom(1024))
    strongpw = re.compile(r'^(?=%s)(?=%s)(?=%s)(?=%s).{%s}$'
                          % (uppers, lowers, numers, spchar, pwlength))
    while True:
        usrpw = ''.join(random.choice(allowchar) for i in range(pwlength))
        if strongpw.match(usrpw):
            return usrpw


@task
def adduser(gp=True):
    """ Adds Users specified by 'users' & creates group
    :param gp: Set True if password should be the same on all hosts
    :return: Nothing

    Usage:
        Global passwords across all hosts
        $ fab adduser
        Different password for each hosts:
        $ fab adduser:gp=False
    """
    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        for group in groups.split(','):
            addgroup = sudo("groupadd %s" % group)
            if addgroup.return_code == 0:
                print("Group added %s: " % group)
            elif addgroup.return_code == 9:
                print("Group already exists: %s" % group)
            else:
                print("An error occurred while adding group: %s" % group)
    for i in users:
        if len(i) == 3:
            pw = generatepw()
            i.append(pw)
        with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
            sudo("adduser -c \"%s - %s\" -m -G %s %s"
                 % (i[0], i[1], groups, i[2]))
            crypted_password = crypt.crypt(i[3],
                                           crypt.mksalt(crypt.METHOD_CRYPT))
            sudo('usermod --password %s %s' % (crypted_password,
                                               i[2]), pty=True)
            # Modify the following rules to your needs: (Read chage manpage)
            sudo("chage -E -1 -W 11 -m 7 -M 42 -I 30 -d now-44days %s" % i[2])
    print("\nUsers for %s\n" % env.host)
    for i in users:  # Print the list of Users with credentials
        print("%s" % i[0])
        print("User: %s\nPassword: %s" % (i[2], i[3]))
    if not gp:
        for i in users:
            if len(i) == 4:
                i.pop()


@task
def mod_comment(user=None, comment=None):
    """ Add/Modify comment for user account
    :param user: username
    :param comment: New comment string
    :return: Nothing
    """
    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        if all([user, comment]):
            userchk = run("id %s" % user)
            if userchk.return_code == 0:
                sudo("usermod -c \"%s\" %s" % (comment, user))
            else:
                print("Account not found on server: %s" % env.host)
        else:
            sys.exit("\nInvalid Params:\nUser: %s\nComment: %s\n"
                     % (user, comment))


@task
def deluser():
    """ Removes users specified by 'users' & leaves group intact
    :return: Nothing
    """
    for i in users:
        sudo("userdel -r %s" % i[2])
