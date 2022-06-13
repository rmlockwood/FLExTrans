#
#   SetWorkingProject.py
#
#   Ron Lockwood
#   SIL International
#   5/10/2022
# 
#   Change the file FTPaths.py in the FlexTools folder to reflect the current
#   work project folder.
#
#   Version 3.5 - 5/10/22 - Ron Lockwood
#    Initial version
#
import os

FTPATHS_FILE = '..\\..\\..\\FlexTools\\FTPaths.py'
COLLECTIONS_PATH_STR = 'COLLECTIONS_PATH'
CONFIG_STR = 'CONFIG_PATH'
FLEX_TOOLS_INI = '"flextools.ini"'
COLLECTIONS_STR = '"Collections"'
LOCAL_CONFIG_PATH_STR = 'Config'

#----------------------------------------------------------------
if __name__ == '__main__':

	# Get the current folder
	currFolder = os.getcwd()
	
	# Get the parent folder
	parentFolder = os.path.dirname(currFolder)
	
	# Add the Config folder name to the path, after going up one level
	localConfigFolder = os.path.join(parentFolder, LOCAL_CONFIG_PATH_STR).replace('\\','\\\\')
	
	# Open the FTPaths.py file
	f = open(FTPATHS_FILE, "r", encoding='utf-8')
	
	# Read all the lines
	lines = f.readlines()
	f.close()
	
	# Open the paths file for write
	f = open(FTPATHS_FILE, "w", encoding='utf-8')
	
	# Loop through all lines
	for line in lines:
		
		# if we have collections line insert the current work project path
		if line.find(COLLECTIONS_PATH_STR) >= 0:
			
			f.write(f'{COLLECTIONS_PATH_STR} = os.path.join("{localConfigFolder}", {COLLECTIONS_STR})\n')
			
		# Same if we have the config_path line
		elif line.find(CONFIG_STR) >= 0:
			
			f.write(f'{CONFIG_STR} = os.path.join("{localConfigFolder}", {FLEX_TOOLS_INI})\n')

		# Otherwise write out the same as the input
		else:
			f.write(line)
			
	f.close()