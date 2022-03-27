#!/usr/bin/env python

'''
This file for first test task
'''

#import Netbox API Library
import pynetbox
import os
from tabulate import tabulate

NETBOX_URL='https://77.223.122.241'
TOKEN = '34bf9f64fe7381fb287234aa186164e5b3920582'
os.environ['REQUESTS_CA_BUNDLE'] = 'netbox.crt'

nb = pynetbox.api(url=NETBOX_URL, token=TOKEN)

#Get vlans object
vlans = nb.ipam.vlans.all()
# Print in tabular some parameters of internal objects:
active_vlans=[]
deprecated_vlans=[]
reserved_vlans=[]
for vlan in vlans:
    if vlan.status.value=='active':
        active_vlans.append(vlan.display)
    if vlan.status.value=='deprecated':
        deprecated_vlans.append(vlan.display)
    if vlan.status.value=='reserved':
        reserved_vlans.append(vlan.display)

print(tabulate({'active':active_vlans,'deprecated':deprecated_vlans,'reserved':reserved_vlans},headers='keys',tablefmt='grid'))



