#to create the whole network. Seems unnecessary
neutron net-create ext-net --shared --router:external=True
neutron subnet-create ext-net 10.1.3.0/24 --name ext-subnet --allocation-pool start=10.1.3.0,end=10.1.3.255 --disable-dhcp

#creating network for each tenant
- neutron_network: name=external_network state=present
                   provider_network_type=local router_external=yes
                   login_username=admin login_password=admin login_tenant_name=admin