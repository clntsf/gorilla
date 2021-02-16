#!/usr/bin/env python3

version = 1.10

import tkinter as tk
from tkinter import filedialog
import pandas as pd
import sys; import os
import requests

versionSourceUrl = 'https://raw.githubusercontent.com/ctsf1/gorilla/main/latest_version.txt'
codeSourceUrl = 'https://raw.githubusercontent.com/ctsf1/gorilla/main/gorilla.py'

default_headers = ['Trial Number', 'Response', 'Zone Type'] # List of default columns, add columns in as needed. Columns listed here but not in the excel sheet will not be included
user_cmds = ['getCols', 'getDefaultCols', 'setDefaultCols', 'addDefaultCols', 'removeDefaultCols', 'help'] # List of commands the user can input to perform special functions. ** Should not be edited under most circumstances **
user_colsText = f'\nList of Column headers in selected sheet: \n' # Header for the getCols function, which displays all columns in the selected sheet
user_helpText = '' 

def checkIfNewest():
	newestVersion = float(str(requests.get(versionSourceUrl, allow_redirects=True).content)[2:-3])
	if newestVersion > version:
		print('A newer version of this program is available. This program will stop and automatically update')
		newVersion = requests.get(codeSourceUrl, allow_redirects = True)
		open(__file__, 'wb').write(newVersion.content)
	else: pass
		

# Takes in arguments passed to terminal and determines the function to perform #######################################################################

def getRuntype():
	
	runtypes = [item for item in user_cmds if item in sys.argv] # 			>	gets list of all defined commands included in user terminal input
	if len(runtypes) == 0: return 'standard' # 												>	if none are referenced, program runs the get_responses function
	elif len(runtypes) == 1: return runtypes[0] # 										>	if one is referenced, the program runs that function
	else: return args[min([args.index(item) for item in runtypes])] #			>	if more than one is referenced, program defaults to the first one mentioned

def getData(): # Gets the dataframe from the excel sheet ##########################################################################################

	root = tk.Tk(); root.withdraw()
	
	file_path = filedialog.askopenfilename()
	if file_path == '': return None
	return file_path

# Changes default headers set in the list in this file through the user's input in terminal ###################################################################
	
def setDefaultHeaders(newHeaders):

	reader = open(__file__, 'r'); lines = reader.readlines(); reader.close()
	
	headersLine = [line for line in lines if 'default_headers' in line][0]
	headersLineIndex = lines.index(headersLine)
	
	sep1, sep2 = headersLine.index('['), headersLine.index(']')+1
	varAssign, defaultHeadersList, afterList = headersLine[:sep1], headersLine[sep1:sep2], headersLine[sep2:]
	
	newHeadersList = '[' + ', '.join([f"'{header}'" for header in newHeaders]) + ']'
	lines[headersLineIndex] = varAssign + newHeadersList + afterList
	writer = open(__file__,'w'); writer.writelines([line for line in lines]); writer.close(); 
	return newHeadersList
	
# Master function for special runtype commands ################################################################################################

def doSpecialRuntype(runtype):
	
	if runtype == 'getCols':
		df = pd.read_excel(getData()); df_cols = [col for col in df]
		print(user_colsText); {print(f'{i+1}. {df_cols[i]}') for i in range(len(df_cols))}
		
	elif runtype == 'getDefaultCols':
		{print(col) for col in default_headers}
		
	elif runtype == 'setDefaultCols':
		
		args = sys.argv[2:]
		if len(args) == 0: args = input('Input new default headers, separated by commas: \n')
		else: args = ' '.join(args)
		if ',' in args: args = args.split(',')
		else: args = [args]
		newHeaders = [item.lstrip(' ') for item in args]
		
		userConfirmation = (input(f'Are you sure you wish to change the current default columns to {newHeaders}? (Y/N)  ') == 'Y')
		if userConfirmation: print(f'Default columns replaced. New default columns are {setDefaultHeaders(newHeaders)}'); return
		else: print(f'Current default columns have been preserved. they are {default_headers}'); return
		
	elif runtype == 'addDefaultCols':
		
		args = sys.argv[2:]
		if len(args) == 0: args = input('Input default headers to add, separated by commas: \n')
		else: args = ' '.join(args)
		if ',' in args: args = args.split(',')
		else: args = [args]
		newHeaders = [item.lstrip(' ') for item in args]
		
		userConfirmation = (input(f'Are you sure you wish to add the column(s) {newHeaders} to the list of default columns? (Y/N)  ') == 'Y')
		if userConfirmation: print(f'Added {newHeaders} to default columns. Default columns are {setDefaultHeaders(default_headers + newHeaders)}'); return
		else: print(f'Current default columns have been preserved. they are {default_headers}'); return
		
	elif runtype == 'removeDefaultCols':
		
		args = sys.argv[2:]
		if len(args) == 0: args = input('Input default headers to remove, separated by commas: \n')
		else: args = ' '.join(args)
		if ',' in args: args = args.split(',')
		else: args = [args]
		removeHeaders = [item.lstrip(' ') for item in args]
		nOverlap = [item for item in removeHeaders if item.upper() not in [col.upper() for col in default_headers]]
		
		if nOverlap == removeHeaders:
			print(f'None of these columns ({removeHeaders}) were found in the list of default headers ({default_headers}). \n> if you meant to add to or replace the current default columns try addDefaultCols or setDefaultCols')
			return
		userConfirmation = (input(f'Are you sure you wish to remove the column(s) {removeHeaders} from the list of default columns? (Y/N)  ').upper() == 'Y')
		if userConfirmation:
			print(f'Removed {removeHeaders} from default columns. Current default columns are {setDefaultHeaders([col for col in default_headers if col.upper() not in [ncol.upper() for ncol in removeHeaders]])}')
			if len(nOverlap) > 0: print(f'Column(s) {nOverlap} were not found in the list of default headers, so they were ignored')
		else: print(f'Current default columns have been preserved. they are {default_headers}')
		return
		
	elif runtype == 'help':
		print(user_helpText); return

def get_responses(output_type='xlsx', headers=default_headers, clean_results=True, show_index = False):
	
	# Takes terminal args and converts them to function params, giving them priority over those written in-file ################################################

	if len(sys.argv) > 1: output_type = sys.argv[1]
	clean_results = (not 'nclean' in sys.argv) and clean_results
	show_index = ('index' in sys.argv) or show_index
	
	# Gets and processes the sheet, and makes a datatable out of the relevant rows from the selected columns
	
	file_path = getData(); df = pd.read_excel(file_path); 
	if type(df) == 'NoneType': print('Failed to enter a filepath.'); return # gets dataframe, and checks whether it's empty
	
	key = [['Zone Name', 'Response'], ['Screen Name', 'response']]['response_button_text' in list(df['Zone Type'])]
	capsHeaders = [item.upper() for item in headers]
	
	newdf = pd.DataFrame(data={col:[df[col][i] for i in range(len(df[col])) if df[key[0]][i] == key[1]] for col in df.columns if col.upper() in capsHeaders})
	
	if clean_results: #																													> Cleans up the outputted dataframe (mostly QOL)
		if 'Correct' in newdf: newdf['Correct'] = [bool(item) for item in newdf['Correct']] #					> replaces integer truth values (0/1) with bools (TRUE/FALSE)
		if 'Trial Number' in newdf: #																										> replaces floating point trial number values with ints, and renames the column to 'Trial' for simplicity
			newdf['Trial Number'] = [int(item) for item in newdf['Trial Number']]
			newdf = newdf.rename(columns={'Trial Number': 'Trial'})
	
	# Output handling for different output types (to terminal as string, to input sheet currently supported)
	
	if output_type == 'string': #																											> Outputs as a string printed to terminal
		stringdf = newdf.to_string(index=show_index)
		print(stringdf); return
	if output_type == 'xlsx': #																												> Outputs as a new sheet in the selected workbook
		writer = pd.ExcelWriter(file_path, mode='a', engine='openpyxl'); sheet_name = 'output' 
		newdf.to_excel(writer, sheet_name, index=show_index, startrow=1, startcol=1) 
		writer.save()
	else: print('Invalid output type. Check your arguments'); return #												> Handles invalid input types											

# Main function ########################################################################################################################

def main():
	checkIfNewest()
	runtype = getRuntype()
	if runtype == 'standard': get_responses()
	else: doSpecialRuntype(runtype)

main()
