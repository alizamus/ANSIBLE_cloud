#!/usr/bin/python

import sys
import os


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
	print 'Please enter the first user number to create'
	start_user = raw_input()
	print 'Please enter the final user number to create'
	end_user = raw_input()
	print 'Do you want the images to be created? (yes or no)?'
	image_q = raw_input()
	if image_q == 'yes':
		image_q = 'true'
	else:
		image_q = 'false'
	f = open('config_vars.yml', 'w')
	f.write('number_of_projects: '+ str(num_of_projects))	
	f.write('\n')
	f.write('data_center_nummber: '+ str(data_center_num))
	f.write('\n')
	f.write('admin_pass: '+ admin_pass)
	f.write('\n')
	f.write('route_target: '+ route_target)
	f.write('\n')
	f.write('start_user: '+ start_user)
	f.write('\n')
	f.write('end_user: '+ end_user)
	f.write('\n')
	f.write('image: '+ image_q)
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
        command = 'ssh-keygen -R ' + str(config_IP)
        os.system(command)
	print '<<<<<<<<<< configuration is done >>>>>>>>>>'
	print '<<<<<<<<<< Now you can run this command: >>>>>>>>>> '
	print '<<<<<<<<<< ansible-playbook test.yml >>>>>>>>>>'
