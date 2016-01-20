
**Create openstack instance**
-----------------------------

This scripts spins up a instance on your openstack installation via command line.


----------


USAGE
-----

 1. You can use virtualenv to test this script. 
 2. You can execute it directly on openstack installation.

**Virtualenv setup:**

Needs the following package to be present on your environment

     gcc
     python-devel
     python-virtualenv
     python-pip

Create  virtualenv and activate

    virtualenv test
    cd test
    source bin/activate
 
 Download the file
 

     cd openstack-create-instance
     pip install -r requirements.txt

Update config.ini based on your openstack environment and it should be on its location

    [ACCOUNT_CREDENTIALS]
    OS_USERNAME=admin
    OS_PASSWORD=Password
    API_KEY=Password
    PROJECT_ID=admin
    OS_TENANT_NAME=admin
    OS_AUTH_URL=http://10.20.30.40:5000/v2.0/

Execute the command 

    python create-instance.py

This would prompt you with the at least steps to boot up the instance

![ScreenShot](https://github.com/mohi048/openstack-create-instance/blob/master/snapshot-create-instance.png)

