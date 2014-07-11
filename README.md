fabric-adduser
==============

#### Fabric script for adding multiple users to a list of servers. 
This script also allows the administrator to set the same unique password for 
each user accross all servers if desired. (see addusr params)

#####Note:
All new accounts are expired by default and will force each user to reset
their password upon first login. Users have approximatly 30 days to login
and change their temporary password or the account will turn inactive.


#### Dependancies:

- fabric api
- makepasswd utility

#### Usage:

Add users:

```
$ fab addusr
```

Add users with persistant passwords:

```
$ fab addusr:pp=True
```

Remove users and leave groups intact.

```
$ fab delusr
```

###### Warning: 
Do not run as parallel as passwords are only generated once for initial server
to allow persistant temporary password for all hosts being processed.

