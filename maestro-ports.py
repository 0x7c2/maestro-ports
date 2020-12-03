#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

import json
import subprocess

ports = {}

proc = subprocess.Popen('sx_api_ports_dump.py', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
out  = proc.stdout.read().split('\n')
for line in out:
	if '0x' in line:
		tmp = line.strip('\n')
		cols = tmp.split('|')
		ports[cols[3].strip()] = { 'port': cols[2].strip(), 'admin_s': cols[5].strip(), 'oper_s': cols[6].strip(), 'module_s': cols[7].strip(), 'oper_speed': cols[9].strip() }

lldp = {}

int = ""
proc = subprocess.Popen('lldpctl', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
out  = proc.stdout.read().split('\n')
for line in out:
	if '-------------' in line:
		if int != "":
			lldp[int] = { 'SysDescr': desc, 'PortDescr': port, 'SysName': sysname }
	tmp = line.strip('\n').split(',')
	if 'Interface' in line:
		int = tmp[0].split(':')[1].strip()[2:]
	if 'SysName' in line:
		sysname = tmp[0].split(':')[1].strip()
	if 'SysDescr' in line:
		desc = tmp[0].split(':')[1].strip().split('/')[0]
		if '#' in desc:
			desc = desc[5:-1]
		else:
			desc = ""
	if 'PortDesc' in line:
		port = tmp[0].split(':')[1].strip()

formatting = "|%5s|%10s|%8s|%8s|%10s|%15s|%15s|%15s|%15s|"

with open("/etc/maestro.json", "r") as read_file:
	m = json.load(read_file)
	print formatting % ( 'port', 'label_port', 'admin_s', 'oper_s', 'oper_speed', 'type', 'name', 'serial', 'PortDescr' )
	print 111*"-"
	for port in m["ports"]:
		if m["ports"][port]["type"] == "downlink":
			if port in lldp:
				sys = lldp[port]['SysDescr']
				por = lldp[port]['PortDescr']
				sysname = lldp[port]['SysName']
			else:
				sys = ""
				por = ""
				sysname = ""
			print formatting % (ports[port]['port'], m["ports"][port]["label"], ports[port]['admin_s'], ports[port]['oper_s'], ports[port]['oper_speed'], m["ports"][port]['type'], sysname, sys, por)
