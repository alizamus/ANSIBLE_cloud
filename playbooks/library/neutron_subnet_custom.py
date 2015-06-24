#!/usr/bin/python
#coding: utf-8 -*-

# (c) 2013, Benno Joy <benno@ansibleworks.com>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/>.

# Revision by Ali Reza Zamani

try:
    from neutronclient.neutron import client
    from keystoneclient.v2_0 import client as ksclient
except ImportError:
    print("failed=True msg='neutron and keystone client are required'")

DOCUMENTATION = '''
---
module: neutron_subnet
version_added: "1.2"
short_description: Add/Remove floating IP from an instance
description:
   - Add or Remove a floating IP to an instance
options:
   login_username:
     description:
        - login username to authenticate to keystone
     required: true
     default: admin
   login_password:
     description:
        - Password of login user
     required: true
     default: True
   login_tenant_name:
     description:
        - The tenant name of the login user
     required: true
     default: True
   auth_url:
     description:
        - The keystone URL for authentication
     required: false
     default: 'http://127.0.0.1:35357/v2.0/'
   region_name:
     description:
        - Name of the region
     required: false
     default: None
   state:
     description:
        - Indicate desired state of the resource
     choices: ['present', 'absent']
     default: present
   network_name:
     description:
        - Name of the network to which the subnet should be attached
     required: true
     default: None
   cidr:
     description:
        - The CIDR representation of the subnet that should be assigned to the subnet
     required: true
     default: None
   tenant_name:
     description:
        - The name of the tenant for whom the subnet should be created
     required: false
     default: None
   ip_version:
     description:
        - The IP version of the subnet 4 or 6
     required: false
     default: 4
   enable_dhcp:
     description:
        - Whether DHCP should be enabled for this subnet.
     required: false
     default: true
   no_gateway:
     description:
        - If "true", no gateway will be created for this subnet
     required: false
     default: false
   gateway_ip:
     description:
        - The ip that would be assigned to the gateway for this subnet
     required: false
     default: None
   dns_nameservers:
     description:
        - DNS nameservers for this subnet, comma-separated
     required: false
     default: None
   allocation_pool_start:
     description:
        - From the subnet pool the starting address from which the IP should be allocated
     required: false
     default: None
   allocation_pool_end:
     description:
        - From the subnet pool the last IP that should be assigned to the virtual machines
     required: false
     default: None
   ipv6-ra-mode:
     description:
        - IPv6 router advertisement mode: dhcpv6-stateful,dhcpv6-stateless,slaac
     required: false
     default: none
   ipv6-address-mode:
     description:
        - IPv6 address mode: dhcpv6-stateful,dhcpv6-stateless,slaac
     required: false
     default: none
   host_routes:
     description:
        - Host routes for this subnet, list of dictionaries, e.g. [{destination: 0.0.0.0/0, nexthop: 123.456.78.9}, {destination: 192.168.0.0/24, nexthop: 192.168.0.1}]
     required: false
     default: None
requirements: ["neutron", "keystoneclient"]
'''

EXAMPLES = '''
# Create a subnet for a tenant with the specified subnet
- neutron_subnet: state=present login_username=admin login_password=admin
                  login_tenant_name=admin tenant_name=tenant1
                  network_name=network1 name=net1subnet cidr=192.168.0.0/24"
'''

_os_keystone = None
_os_tenant_id = None
_os_network_id = None

def _get_ksclient(module, kwargs):
    try:
        kclient = ksclient.Client(
            username=module.params.get('login_username'),
            password=module.params.get('login_password'),
            tenant_name=module.params.get('login_tenant_name'),
            auth_url=module.params.get('auth_url'),
            region_name=module.params.get('region_name'))
    except Exception as e:
        module.fail_json(msg = "Error authenticating to the keystone: %s" %e.message)
    global _os_keystone
    _os_keystone = kclient
    return kclient


def _get_endpoint(module, ksclient):
    try:
        endpoint = ksclient.service_catalog.url_for(service_type='network', endpoint_type='publicURL')
    except Exception as e:
        module.fail_json(msg = "Error getting endpoint for glance: %s" % e.message)
    return endpoint

def _get_neutron_client(module, kwargs):
    _ksclient = _get_ksclient(module, kwargs)
    token = _ksclient.auth_token
    endpoint = _get_endpoint(module, _ksclient)
    kwargs = {
            'token': token,
            'endpoint_url': endpoint
    }
    try:
        neutron = client.Client('2.0', **kwargs)
    except Exception as e:
        module.fail_json(msg = " Error in connecting to Neutron: %s" % e.message)
    return neutron

def _set_tenant_id(module):
    global _os_tenant_id
    if module.params['tenant_name']:
        # We need admin power in order retrieve the tenant_id of a given
        # tenant name and to create/delete networks for a tenant that is not
        # the one used to authenticate the user.
        tenant_name = module.params['tenant_name']
        for tenant in _os_keystone.tenants.list():
            if tenant.name == tenant_name:
                _os_tenant_id = tenant.id
                break
    else:
        _os_tenant_id = _os_keystone.tenant_id

    if not _os_tenant_id:
        module.fail_json(msg = "The tenant id cannot be found, please check the paramters")

def _get_net_id(neutron, module):
    kwargs = {
        'tenant_id': _os_tenant_id,
        'name': module.params['network_name'],
    }
    try:
        networks = neutron.list_networks(**kwargs)
    except Exception as e:
        module.fail_json(msg = "Error in listing Neutron networks: %s" % e.message)
    if not networks['networks']:
            return None
    return networks['networks'][0]['id']


def _get_subnet_id(module, neutron):
    global _os_network_id
    subnet_id = None
    _os_network_id = _get_net_id(neutron, module)
    if not _os_network_id:
        module.fail_json(msg = "network id of network not found.")
    else:
        kwargs = {
            'tenant_id': _os_tenant_id,
            'name': module.params['name'],
        }
        try:
            subnets = neutron.list_subnets(**kwargs)
        except Exception as e:
            module.fail_json( msg = " Error in getting the subnet list:%s " % e.message)
        if not subnets['subnets']:
            return None
        return subnets['subnets'][0]['id']

def _create_subnet(module, neutron):
    neutron.format = 'json'
    subnet = {
            'name': module.params['name'],
            'ip_version': module.params['ip_version'],
            'enable_dhcp': module.params['enable_dhcp'],
            'tenant_id': _os_tenant_id,
            'gateway_ip': module.params['gateway_ip'],
            'dns_nameservers': module.params['dns_nameservers'],
            'network_id': _os_network_id,
            #'cidr': module.params['cidr'],
            'cidr': '10.1.' + str(module.params['datacenter_number']) + '.' + str((int(module.params['user_number']))*8) +'/29',
            'host_routes': module.params['host_routes'],
    }
    if module.params['allocation_pool_start'] and module.params['allocation_pool_end']:
        allocation_pools = [
            {
                'start' : module.params['allocation_pool_start'],
                'end' : module.params['allocation_pool_end']
            }
        ]
        subnet.update({'allocation_pools': allocation_pools})
    # "subnet['gateway_ip'] = None" means: "no gateway"
    # no gateway_ip in body means: "automatic gateway"
    if module.params['no_gateway']:
        subnet['gateway_ip'] = None
    elif module.params['gateway_ip'] is not None:
        subnet['gateway_ip'] = module.params['gateway_ip']
    if module.params['dns_nameservers']:
        subnet['dns_nameservers'] = module.params['dns_nameservers'].split(',')
    else:
        subnet.pop('dns_nameservers')
    if not module.params['host_routes']:
        subnet.pop('host_routes')
    if module.params['ipv6_ra_mode'] and int(module.params['ip_version']) == 6:
        subnet.update({'ipv6_ra_mode': module.params['ipv6_ra_mode']})
    if module.params['ipv6_address_mode'] and int(module.params['ip_version']) == 6:
        subnet.update({'ipv6_address_mode': module.params['ipv6_address_mode']})
    try:
        new_subnet = neutron.create_subnet(dict(subnet=subnet))
    except Exception, e:
        module.fail_json(msg = "Failure in creating subnet: %s" % e.message)
    return new_subnet['subnet']['id']


def _delete_subnet(module, neutron, subnet_id):
    try:
        neutron.delete_subnet(subnet_id)
    except Exception as e:
        module.fail_json( msg = "Error in deleting subnet: %s" % e.message)
    return True


def main():

    ipv6_mode_choices = ['dhcpv6-stateful', 'dhcpv6-stateless', 'slaac']
    module = AnsibleModule(
        argument_spec = dict(
            login_username = dict(default='admin'),
            login_password = dict(required=True),
            login_tenant_name = dict(required='True'),
            auth_url = dict(default='http://127.0.0.1:35357/v2.0/'),
            region_name = dict(default=None),
            name = dict(required=True),
            network_name = dict(required=True),
            cidr = dict(default=None),
            tenant_name = dict(default=None),
            state = dict(default='present', choices=['absent', 'present']),
            ip_version = dict(default='4', choices=['4', '6']),
            enable_dhcp = dict(default=True, type='bool'),
            no_gateway = dict(default=False, type='bool'),
            gateway_ip = dict(default=None),
            dns_nameservers = dict(default=None),
            allocation_pool_start = dict(default=None),
            allocation_pool_end = dict(default=None),
            ipv6_ra_mode = dict(default=None, choices=ipv6_mode_choices),
            ipv6_address_mode = dict(default=None, choices=ipv6_mode_choices),
            host_routes = dict(default=None),
            user_number = dict(required=True),
            datacenter_number = dict(required=True)
        ),
    )
    neutron = _get_neutron_client(module, module.params)
    _set_tenant_id(module)
    if module.params['state'] == 'present':
        subnet_id = _get_subnet_id(module, neutron)
        if not subnet_id:
            subnet_id = _create_subnet(module, neutron)
            module.exit_json(changed = True, result = "Created" , id = subnet_id)
        else:
            module.exit_json(changed = False, result = "success" , id = subnet_id)
    else:
        subnet_id = _get_subnet_id(module, neutron)
        if not subnet_id:
            module.exit_json(changed = False, result = "success")
        else:
            _delete_subnet(module, neutron, subnet_id)
            module.exit_json(changed = True, result = "deleted")

# this is magic, see lib/ansible/module.params['common.py
from ansible.module_utils.basic import *
main()
