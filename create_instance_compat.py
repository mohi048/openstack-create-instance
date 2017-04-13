# pip install pytz==2016.10 , prettytable==0.7.2 , shade==1.16.0
# compatble with python-2 and python-3

from six.moves import input
from prettytable import PrettyTable
from datetime import datetime
from shade import *
import sys
import time


def inital_setup():
    simple_logging(debug=True)
    try:
        connection = openstack_cloud(cloud=sys.argv[1])
    except IndexError as e:
        print("Missing cloud params , check clouds.yaml")
        sys.exit()
    return connection

def tables_format(spec_name, spec_params):
    ids = []
    print ("Listing "+spec_name+' :')
    table = PrettyTable([spec_name+'_ID', spec_name+'_Name'])
    if spec_name != 'Network':
        for items in spec_params:
            ids.append(items.id)
            table.add_row([items.id, items.name])
        print(table)
        sel_usr_val = selected_values(spec_name)
    else:
        for items in spec_params:
            ids.append(items['id'])
            table.add_row([items['id'], items['name']])
        print(table)
        sel_usr_val = selected_values(spec_name)
    if sel_usr_val in ids:
        return sel_usr_val
    else:
        print("Enter the correct "+spec_name+"_ID")
        sys.exit()


def selected_values(spec_name):
    sel_option = input(" Enter the "+spec_name+"_ID : ")
    return sel_option


def create_instance(conn,image_id, flavor_id, external_network):
    instance_name = input("Enter the instance name to be created :")
    startTime = datetime.now()
    testing_instance = conn.create_server(wait=False,
        auto_ip=True, name=instance_name, image=image_id,
        flavor=flavor_id, network=external_network)
    while conn.get_server(testing_instance.id).vm_state == 'building':
        print("preparing the instance to boot")
        print("Time elapsed since ", str(datetime.now() - startTime))
        time.sleep(2)
        print("Status = ", conn.get_server(testing_instance.id).vm_state)
    print("="*60)
    print("Server created with id = ", testing_instance.id)
    print("Total time taken to build this instance ", str(datetime.now() - startTime))
    print("="*60)


def main():
    conn = inital_setup()
    images = conn.list_images()
    use_image_id = tables_format('Image', images)

    flavors = conn.list_flavors()
    use_flavor_id = tables_format('Flavor', flavors)

    networks = conn.list_networks()
    use_network_id = tables_format('Network', networks)

    create_instance(conn,use_image_id, use_flavor_id, use_network_id)


if __name__ == "__main__":
    main()    