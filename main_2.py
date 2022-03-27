#!/usr/bin/env python

'''
This file for second test task
'''

import yaml
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)
from datetime import datetime


ERASE_CONFIG_STRING = 'default interface '
CHECK_CONFIG_STRING = 'sh run interface '


def send_show_command(device, commands):
    '''
    Send show commands to check/verify configuration
    :param device: dictionary with params of connection
    :param commands: list of commands
    :return: output of commands
    '''
    result = {}
    try:
        with ConnectHandler(**device,conn_timeout=10) as ssh:
            ssh.enable()
            for command in commands:
                output = ssh.send_command(command)
                result[command] = output
        return result
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(error)

def configure_item(device,commands):
    '''
    Send configuration commands
    :param device: dictionary with params of connection
    :param commands: list of commands
    :return:
    '''
    try:
        with ConnectHandler(**device,conn_timeout=10) as ssh:
            ssh.enable()
            output = ssh.send_config_set(commands)
            result = output
        return result
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(error)


if __name__ == "__main__":

#Load with YAML parameters for connection
    with open('params.yaml') as f:
        switches = yaml.safe_load(f)
    with open('commands.yaml') as f:
        config_list = yaml.safe_load(f)
#Interactive user session (input parameters to configure one or range of ports)
    while True:
        interface = input('Please, input interfaces that you want to configure (Gi1/0,Gi1/1,Gi1/2,Gi1/3): ')
        try:
            interface_list = [item.strip() for item in interface.split(',')]
            # If user don't input anything - assume that he want to configure all interfaces
            if interface_list==['']:
                interface_list = ['Gi1/0','Gi1/1','Gi1/2','Gi1/3']
                break
            #Otherwise will check that user insert correct range
            corr = True
            for item in interface_list:
                if any([len(item)>5,item[:4].lower()!='gi1/', int(item[4:])>3]):
                    corr = False
                    break
            if not corr:
                print('Incorrect range, only suggested interfaces supported to configure...')
                continue
            break
        except(ValueError) as err:
            print('Incorrect input\n'+str(err))
            continue
# Create list of commands withing interfaces
    full_config_list = []
    for intf in interface_list:
        full_config_list.append(f'interface {intf}')
        full_config_list.extend(config_list)

# Ask user interactively - what he is want to do (configure interfaces or erase config)?
    choice = input(f'\nDo you want configure this interfaces {str(interface_list)} or erase them to default? [erase\configure]: ')
    if 'er' in choice.lower():
        choice = 'erase'
        print('\nPlease, waiting for a minute. Collecting actual information... ')
# Double check - which configuration we will erase
        start_time = datetime.now()
        with ThreadPoolExecutor(max_workers=5) as executor:
            result = executor.map(send_show_command,switches,repeat([CHECK_CONFIG_STRING+intf for intf in interface_list]))
            for device,output in zip(switches,result):
                print('='*50,'HOST : '+device['host'],'PORT : '+str(device['port']),sep='\n')
                for key,value in output.items():
                    print('*'*10+key+'*'*10,sep=' ')
                    print(value)
                print('='*50)
        print('overall time to collect info -->', datetime.now()-start_time)
    elif 'con' in choice.lower():
        choice = 'configure'
        pprint(full_config_list)
    else:
        print("Don't understand input of your choice - operation aborted...")
        exit()

# Ask user to double check - is he understand his action?
    print(f'\n{"^^ This configuration will be apply ^^" if choice=="configure" else "^^ Interfaces now with following configuration ^^"}')
    print('\nCheck configuration above')
    sure = input(f'\nDo you sure with your choice ({choice})? [y(es)/n(o)/c(ancel)] : ')
    if any(['n' in sure.lower()[0],'c' in sure.lower()[0]]):
        print(30*'-','\n Operation aborted !')
        exit()
    if 'y' in sure.lower()[0]:
#Configure ports
        if choice == 'configure':
            print(50*'-','\nHave been started to implement configuration - waiting for a while...\n')
            start_time = datetime.now()
            with ThreadPoolExecutor(max_workers=5) as executor:
                result = executor.map(configure_item,switches,repeat(full_config_list))
                for device,output in zip(switches,result):
                    print('+'*50,'HOST : '+device['host'],'PORT : '+str(device['port']),sep='\n')
                    print(output)
                    print('+'*50)
            print('overall time to configure -->', datetime.now()-start_time)
#Erase ports
        if choice == 'erase':
            start_time = datetime.now()
            with ThreadPoolExecutor(max_workers=5) as executor:
                result = executor.map(configure_item,switches,repeat([ERASE_CONFIG_STRING+intf for intf in interface_list]))
                for device,output in zip(switches,result):
                    print('+'*50,'HOST : '+device['host'],'PORT : '+str(device['port']),sep='\n')
                    print(output)
                    print('+'*50)
            print('overall time to erase config -->', datetime.now()-start_time)









