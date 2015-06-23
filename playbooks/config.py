#!/usr/bin/python

import sys



if __name__ == '__main__':
	print '<<<<<<<<<< start of configuration >>>>>>>>>>'
	print 'How many projects would you like to have?'
	num_of_projects = input()
	if num_of_projects > 32:
		print "Not enough floating IP for the users"
		sys.exit()
	print 'Please enter the data center number'
	data_center_num = input()
	print 'Please enter the admin pass for openstack'
	admin_pass = raw_input()
	print 'Please enter the route target'
	route_target = raw_input()
	f = open('config_vars.yml', 'w')
	f.write('number_of_projects: '+ str(num_of_projects))	
	f.write('\n')
	f.write('data_center_nummber: '+ str(data_center_num))
	f.write('\n')
	f.write('admin_pass: '+ admin_pass)
	f.write('\n')
	f.write('route_target: '+ route_target)
	f.close()
	print 'Enter the IP of the config node'
	config_IP = raw_input()
	print 'Enter the username for config node. e.g:root'
	config_user = raw_input()
	print 'Enter the password for above user in config node.'
	config_pass = raw_input()
	f = open('inventory', 'w')
	f.write('[cloud]\n')
	f.write('cloud1')
	f.write(' ')
	f.write('ansible_ssh_host=' + config_IP)
	f.write(' ')
	f.write('ansible_ssh_port=22')
	f.write(' ')
	f.write('ansible_ssh_user=' + config_user)
	f.write(' ')
	f.write('ansible_ssh_pass=' + config_pass)
	f.write(' ')
	f.write('ansible_sudo_pass=' + config_pass)
	f.close()
	print '<<<<<<<<<< configuration is done >>>>>>>>>>'
	print '<<<<<<<<<< Now you can run this command: >>>>>>>>>> '
	print '<<<<<<<<<< ansible-playbook test.yml >>>>>>>>>>'
