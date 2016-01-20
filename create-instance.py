## Author - Mohit. ((  Git -: http://github.com/mohi048  ))
## Python script to launch instance with user prompts
## Tested in Kilo and Liberty release
## update the config.ini file and execute the python script

import time
from datetime import datetime
import requests
from configparser import SafeConfigParser
from novaclient.v2 import client
from neutronclient.v2_0 import client as neutronClient


parser = SafeConfigParser()
parser.read('./config.ini')
neutron_credentials = {}
neutron_credentials['username'] =  parser.get('ACCOUNT_CREDENTIALS', 'OS_USERNAME')
neutron_credentials['password'] =  parser.get('ACCOUNT_CREDENTIALS', 'OS_PASSWORD')
neutron_credentials['tenant_name'] =  parser.get('ACCOUNT_CREDENTIALS', 'OS_TENANT_NAME')
neutron_credentials['auth_url'] =  parser.get('ACCOUNT_CREDENTIALS', 'OS_AUTH_URL')


nova_credentials = {}
nova_credentials['username'] =  parser.get('ACCOUNT_CREDENTIALS', 'OS_USERNAME')
nova_credentials['api_key'] =  parser.get('ACCOUNT_CREDENTIALS', 'API_KEY')
nova_credentials['project_id'] =  parser.get('ACCOUNT_CREDENTIALS', 'PROJECT_ID')
nova_credentials['auth_url'] =  parser.get('ACCOUNT_CREDENTIALS', 'OS_AUTH_URL')




def inst(values,typ):
	count = 0
	dd = {}
	print "\nListing the %s" %typ
	for value in values:
		#print value
		count+=1
		if typ == 'Network':
			print '['+str(count)+']  ' + value['name']
			dd[count] = value['id']
		elif typ == 'AvailabilityZone':
			if value.zoneName == 'internal':
				print "Skipping the default %s zone" %value.zoneName
				count = 0
			else:
				print '['+str(count)+']  ' + value.zoneName
				dd[count] = value.zoneName
		else:
			print '['+str(count)+']  ' + value.name
			dd[count] = value.id
	#user_input = int(raw_input ("Enter the %s number to boot without brackets : " %typ))
	user_input = raw_input ("Enter the %s number to boot without brackets : " %typ)
	if int(user_input) in dd.keys():
		return dd.get(int(user_input))
	else:
		print dd.get(user_input," ERROR !!!! Could not find the id")
		quit()
	
def create_server(instance_name,img,flv,secu,nets,novaConnection,avz):
	startTime = datetime.now()
	server = novaConnection.servers.create(
		name = instance_name,
		image = img,
		flavor = flv,
		nics = [{'net-id':nets}],
		availability_zone = avz,
		security_groups = [secu])
	server_status = server.status
	ids = server.id
	print "Building Instance ID :: ",ids
	while server_status == 'BUILD':
		print "\n"
		time.sleep(3)
		print "Creating the instance.....with status ",server_status
		print "Time elapsed since ",datetime.now() - startTime
		server = novaConnection.servers.get(server.id)
		server_status = server.status
		print "Instance created with status ", server_status
	print "*"*60
	print " Total Time to execute ",datetime.now() - startTime
	print "*"*60
	instance_created = novaConnection.servers.find(id=server.id)
	print "VM Name = %s\t" % instance_created.name
	for network_type,details in instance_created.addresses.iteritems():
		print "Attached to ",network_type
		for network in details:
			Network_Details = dict(network)
			print "IP Address = %s" %str(Network_Details.get('addr'))
			print "IP Version = %s" %str(Network_Details.get('version'))

try:
	print "\n Attempting to connect on %s" %nova_credentials['auth_url']
	response = requests.get(url=nova_credentials['auth_url'],timeout=(10.0,1))
except requests.exceptions.ReadTimeout as e:
    print e.message
finally:
	print "Connected to the host"

neutronConnection = neutronClient.Client(**neutron_credentials)
novaConnection = client.Client(**nova_credentials)

instance_name= raw_input("\nType the instance name to be created : ")
img = inst(novaConnection.images.list(),'Image')
flv = inst(novaConnection.flavors.list(),'Size')
secu = inst(novaConnection.security_groups.list(),'Security')
avz = inst(novaConnection.availability_zones.list(),'AvailabilityZone')

for nn in neutronConnection.list_networks().values():
	nets = inst(nn,'Network')

if img and flv and secu and nets and instance_name and avz:
	print "Creating the server with specified paramters\n"
	create_server(instance_name,img,flv,secu,nets,novaConnection,avz)
else:
	print "Error , required variables are missing, Please check the above options"
