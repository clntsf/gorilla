import inquirer

msg = 'Add column to list, or enter "DONE" to confirm list: '
premsg = 'Please input columns to {} default columns list, one at a time.'
set_msg = 'replace '; add_msg = 'add to '; remove_msg = 'remove from '

opon = [inquirer.List('run_on',
				message = 'Run program on file or directory?',
				choices = [('File', 'file'), ('Directory','dir')], default = 'file')]
                  
settings = [inquirer.Checkbox('settings',
				message = "Change program settings (SPACE to change, ENTER to confirm)",
				choices =  [('Clean Results', 'c'), ('Show Data table index', 'i')], default = ['c'])]

def newdir(dtype):				
	return [inquirer.List('newdir',
				message = f'Output results to new {dtype} in directory?',
				choices = [('Yes', True), ('No', False)], default = True)]

# Get command user wishes to perform

cmd_get = [inquirer.List('cmd', message='Command to run: ',
					choices=[
					('Run main program', 'std'), ('Display list of all columns in a file/directory', 'get'), ('Set default columns', 'set'),
					('Add to default columns','add'), ('Remove default columns', 'remove'), ('Show help menu', 'help'),])]

def processRuntype():
	global settings
	runtype = inquirer.prompt(cmd_get)['cmd']
	
	if runtype in ['std', 'get']:
		operateOn = inquirer.prompt(opon)['run_on']
		if runtype == 'get': return 'get', operateOn
		else:
			makeNewDir = inquirer.prompt(newdir(['file', 'directory'][operateOn == 'dir']))['newdir']
			settingsList = inquirer.prompt(settings)['settings']; userSettings = [(item in settingsList) for item in settings[0].choices]
			return 'std', [operateOn, makeNewDir, *userSettings]; print(*userSettings)
						
	if runtype in ['set', 'add', 'remove']:
		print(premsg.format(eval(f'{runtype}_msg'))); cols_list = []; newest = input(msg)
		while newest != 'DONE': cols_list.append(newest); newest = input('\r' + msg)
		return runtype, cols_list
		
	else: return 'help', 0