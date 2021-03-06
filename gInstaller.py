#!/usr/bin/env python3

import sys; import os
from subprocess import run

# important directories

homedir = os.getenv("HOME")
realdir = os.path.dirname(os.path.realpath(__file__))

################################################################################################

# make directory, download and move github project (doubles as auto-update)

def getNewest(defaultList=None):
	
	os.system(f'curl -L -O http://github.com/ctsf1/gorilla/archive/main.zip')
	os.system(f'unzip ~/main.zip; mv {__file__} ~/gorilla-main')
	os.system('rm -r ~/bin/gorilla; mv ~/gorilla-main ~/bin/gorilla; rm -rf ~/main.zip')
	os.system('mv ~/bin/gorilla/gorilla.py ~/bin/gorilla/gorilla; chmod +x ~/bin/gorilla/gorilla')
	
	if defaultList != None: # Used for auto-update
		
		main_lines = open(f'{homedir}/bin/gorilla/gorilla.py', 'r').readlines()
		headersLine = [line for line in main_lines if 'default_headers' in line][0]
		lineIndex = main_lines.index(headersLine); sep1, sep2 = headersLine.index('['), headersLine.index(']')+1
		
		listFormat = ''.join(['['] + ["'{}',"] * len(defaultList) + [']'])
		main_lines[lineIndex] = headersLine[:sep1] + listFormat.format(*defaultList) + headersLine[sep2:]
		
		with open(f'{homedir}/bin/gorilla/gorilla.py', 'w') as writer: writer.writelines(main_lines); writer.close()
		
	return

################################################################################################

# Main self-installation function

def main():		

	# put future directory of app into path
	
	with open(homedir+'/.zprofile','r') as reader:
		lines = reader.readlines(); reader.close()
		if 'export PATH=$PATH":$HOME/bin/gorilla"' in lines: pass
		else: writer = open(homedir+'/.zprofile','a'); writer.write('export PATH=$PATH":$HOME/bin/gorilla"'); writer.close()
		
	os.system('mkdir ~/bin'); getNewest()
	os.system('rm -rf ~/gorilla-installer')
		
	# make sure non-standard lib dependencies are downloaded with PIP

	dependencies = ['inquirer', 'pandas']
	
	userHasPip = run(['python3', '-m', 'pip', '--version'], capture_output=True).stdout[:3] == b'pip'
	if not userHasPip:
		os.system('curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py; python3 get-pip.py')
	for item in dependencies:
		os.system(f'pip install -U {item}')
		
	return

if __name__ == '__main__': main()
