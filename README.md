fabric-adduser
==============

#### Fabric script for adding multiple users to a list of servers. 
A standalone script that allows a system administrator to add multiple users 
to multiple hosts and set a global or unique password for each server.

#####Note:
All new accounts are expired by default and will force each user to reset
their password upon first login. Users have approximately 30 days to login
and change their temporary password or the account will turn inactive.


#### Dependencies:

- makepasswd utility
- python-pip

```
$ pip install -r requirements.txt
```

#### Usage:

Add users:

```
$ fab adduser
```

Add users with global password (same password set for all hosts):

```
$ fab adduser:gp=True
```

Remove users and leave groups intact.

```
$ fab deluser
```

###### Warning: 
Do not run as parallel as passwords are only generated once for initial server
to allow global temporary password for all hosts being processed.

