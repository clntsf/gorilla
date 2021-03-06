#!/usr/bin/env python3
version = 1.42

import tkinter as tk; from tkinter import filedialog
import pandas as pd
import sys; import os
import requests
from textwrap import fill
from selector import processRuntype
from gInstaller import getNewest

versionSourceUrl = 'https://raw.githubusercontent.com/ctsf1/gorilla/main/gorilla.py'
default_headers = ['Trial Number', 'Response', 'Zone Type'] # List of default columns, add columns in as needed. Columns listed here but not in the excel sheet will not be included
user_colsText = f'\nList of Column headers in selected sheet: \n' # Header for the getCols function, which displays all columns in the selected sheet
user_helpText = '' 
	
###### AUTO-UPDATING ######

def checkIfNewest():
	nv1 = str(requests.get(versionSourceUrl, allow_redirects=True).content).split('\\n')[1]
	newestVersion = float(nv1[nv1.index('=')+1:])
	return newestVersion == version
		
# Takes in arguments passed to terminal and determines the function to perform #######################################################################

def getData():

	root = tk.Tk(); root.withdraw()
	file_path = filedialog.askopenfilename()
	if file_path == '': return None
	else: return file_path

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

def editDefaultHeaders(mode, userInputMessage, userConfirmationMessage, userConfirmedMessage, userConfirmedVars, userCancelledMessage):
	
	args = sys.argv[2:]
	if len(args) == 0: args = input(fill(userInputMessage, screenWidth))
	else: args = ' '.join(args)	
	if ',' in args: args = args.split(',')
	else: args = [args]	
	headers = [item.lstrip(' ') for item in args]
	
	if mode == 'remove':
		nOverlap = [item for item in headers if item.upper() not in [col.upper() for col in default_headers]]
		if nOverlap == headers:
			print(fill(f'None of these columns ({headers}) were found in the list of default headers ({default_headers}).',screenWidth))
			print(fill('	> if you meant to add to or replace the current default columns try addDefaultCols or setDefaultCols', screenWidth))
			return
	userConfirmation = (input(fill(userConfirmationMessage.format(headers)), screenWidth) == 'Y')
	if userConfirmation:
		print(fill(userConfirmedMessage.format(eval(userConfirmedVars)), screenWidth))
		if mode == 'remove' and len(nOverlap) > 0: print(fill(f'Column(s) {nOverlap} were not found in the list of default headers, so they were ignored', screenWidth))
	else: print(fill(userCancelledMessage.format(default_headers),screenWidth))

def doSpecialRuntype(runtype):
	
	if runtype == 'getCols':
		df = pd.read_excel(getData()); df_cols = [col for col in df]
		print(fill(user_colsText, screenWidth)); {print(f'{i+1}. {df_cols[i]}') for i in range(len(df_cols))}
		
	elif runtype == 'getDefaultCols':
		{print(col) for col in default_headers}
		
	elif runtype == 'set': return editDefaultHeaders('set','Input new default headers, separated by commas: \n',
								    'Are you sure you wish to change the current default columns to {}? (Y/N)  ',
								    'Default columns replaced. New default columns are {}', 'setDefaultHeaders(headers)',
								    'Current default columns have been preserved. they are {}')
		
	elif runtype == 'add': return editDefaultHeaders('add','Input new default headers, separated by commas: \n',
								    'Are you sure you wish to add the column(s) {} to the list of default columns? (Y/N)  ',
								    'Added {} to default columns. Default columns are {}', '[headers, setDefaultHeaders(default_headers + headers)]',
								    'Current default columns have been preserved. they are {}')
		
	elif runtype == 'remove': return editDefaultHeaders('remove','Input new default headers, separated by commas: \n',
								       'Are you sure you wish to remove the column(s) {} from the list of default columns? (Y/N)  ',
								       'Added {} to default columns. Default columns are {}',
								       '[headers, setDefaultHeaders([col for col in default_headers if col.upper() not in [ncol.upper() for ncol in removeHeaders]])]',
								       'Current default columns have been preserved. they are {}')
	
	elif runtype == 'help':
		print(fill(user_helpText, screenWidth)); return

def get_responses(operateOn, makeNewDir, clean_results, show_index):
	
	# Takes terminal args and converts them to function params, giving them priority over those written in-file ################################################

	if len(sys.argv) > 1: output_type = sys.argv[1]
	clean_results = (not 'nclean' in sys.argv) and clean_results
	show_index = ('index' in sys.argv) or show_index
	
	# Gets and processes the sheet, and makes a datatable out of the relevant rows from the selected columns
	
	file_path = getData()
	if file_path == None: return
	df = pd.read_excel(file_path); 
	if type(df) == 'NoneType': print('Failed to enter a filepath.'); return # gets dataframe, and checks whether it's empty
	
	key = [['Zone Name', 'Response'], ['Screen Name', 'response']]['response_button_text' in list(df['Zone Type'])]
	capsHeaders = [item.upper() for item in headers]
	
	newdf = pd.DataFrame(data={col:[df[col][i] for i in range(len(df[col])) if df[key[0]][i] == key[1]] for col in df.columns if col.upper() in capsHeaders})
	
	if clean_results: #																													> Cleans up the outputted dataframe (mostly QOL)
		if 'Correct' in newdf: newdf['Correct'] = [bool(item) for item in newdf['Correct']] #					> replaces integer truth values (0/1) with bools (TRUE/FALSE)
		if 'Trial Number' in newdf: #																										> replaces floating point trial number values with ints, and renames the column to 'Trial' for simplicity
			newdf['Trial Number'] = [int(item) for item in newdf['Trial Number']]
			newdf = newdf.rename(columns={'Trial Number': 'Trial'})

	writer = pd.ExcelWriter(file_path, mode='a', engine='openpyxl'); sheet_name = 'output' 
	newdf.to_excel(writer, sheet_name, index=show_index, startrow=1, startcol=1) 
	writer.save()											

# Main function ########################################################################################################################

def main():
	if checkIfNewest():
		runtype, params = processRuntype(); print(params)
		if runtype == 'std': get_responses(*params)
		else: doSpecialRuntype(runtype)
	else:
		print(fill('A newer version of this program is available. This program will stop and automatically update. Please restart the program on completion', screenWidth))
		getNewest(default_headers)
		print('Update installed successfully.')

screenWidth = os.get_terminal_size().columns
main()
