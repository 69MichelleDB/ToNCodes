import os
import sys
import platform
import getpass
import glob
import Globals as gs
import re
from tkinter import messagebox
from Tools.errorHandler import ErrorLogging

# Verify all folders and files are there
def VerifyInitFileStructure():
    try:
        # Folders
        if os.path.exists(gs._FOLDER_TEMPLATES) == False:
            os.mkdir(gs._FOLDER_TEMPLATES)
        if os.path.exists(gs._FOLDER_CODES) == False:
            os.mkdir(gs._FOLDER_CODES)
        if os.path.exists(gs._FOLDER_LOGS) == False:
            os.mkdir(gs._FOLDER_LOGS)
        if os.path.exists(gs._FOLDER_TEMP) == False:
            os.mkdir(gs._FOLDER_TEMP)
        # Files
        if os.path.exists(gs._CONFIG_FILE) == False:                # Check if there's a config file, if there's none, if the template is there
            if os.path.exists(os.path.join(gs._FOLDER_TEMPLATES,f'{gs._CONFIG_FILE}.default')) == False:
                messagebox.showwarning("Warning", "Templates/config.xml.default not found, please verify your installation")
                sys.exit()
    except Exception as e:
        ErrorLogging(f"Error in VerifyInitFileStructure: {e}")
    

# To avoid uploading my config files we'll have .defaults and just duplicate them if they don't exist
def CreateFromDefault(i_file):
    try:
        if not os.path.exists(i_file):                    # If the file doesn't exist, duplicate the template
            print(f'The {os.path.basename(i_file)} file does not exist, creating...')
            defaultConfigFile = os.path.join(gs._FOLDER_TEMPLATES+os.path.sep, i_file+'.default')
            if os.path.exists(defaultConfigFile):
                with open(defaultConfigFile, 'r') as src, open(i_file, 'w') as dst:
                    dst.write(src.read())
            else:
                raise FileNotFoundError(f"Default template file '{defaultConfigFile}' not found.")
    except Exception as e:
        ErrorLogging(f"Error in CreateFromDefault: {e}")


# Pass it a list of files and obtain a dictionary with the file name and the date modified
def GetDateModified(i_files):
    try:
        filesDict = {}    
        for file in i_files:
            filesDict[file] = os.path.getmtime(file)

        return filesDict
    except Exception as e:
        ErrorLogging(f"Error in GetDateModified: {e}")


# Pass it a pair of dictionaries with current an previous dates, return only the ones we need to check
def GetModifiedFiles(i_currentDates, i_previousDates):
    try:
        filesToCheck = []    
        for file in i_currentDates:
            if file not in i_previousDates or i_currentDates[file] != i_previousDates[file]:    # if the file is new or if the date has changed
                filesToCheck.append(file)
                print(f'{os.path.basename(file)} was modified({i_currentDates[file]}), adding to list')

        return filesToCheck
    except Exception as e:
        ErrorLogging(f"Error in GetModifiedFiles: {e}")


# On first boot, lets try to give a possible valid path for where VRC logs might be
def GetPossibleVRCPath():
    try:
        result = ''

        print(f'Platform: {platform.system()}')
        userName = getpass.getuser()
        print(f'User name: {userName}')
        
        if platform.system() == "Windows":
            result = f'c:\\users\\{userName}\\AppData\\LocalLow\\VRChat\\VRChat\\'
        elif platform.system() == "Linux":

            possiblePaths = (
                            f'/home/{userName}/.steam/debian-installation/steamapps/compatdata/438100/pfx/drive_c/users/steamuser/AppData/LocalLow/VRChat/VRChat/',
                            f'/home/{userName}/.local/share/Steam/steamapps/compatdata/438100/pfx/drive_c/users/steamuser/AppData/LocalLow/VRChat/VRChat/',
                            f'/home/{userName}/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/438100/pfx/drive_c/users/steamuser/AppData/LocalLow/VRChat/VRChat/'
                            )
            for path in possiblePaths:
                if os.path.exists(path):
                    print(f'Valid path {path}')
                    result = path
                    break
        else:
            print('Might be a Mac or something else')

        return result
    except Exception as e:
        ErrorLogging(f"Error in GetPossibleVRCPath: {e}")


# File to be send to discord through the webhook
def CreateNewTempCodeFile(i_folder, i_fileName, i_string):
    try:
        forbiddenChars = r'[\\/:*?"<>|]'                        # We can't allow these characters in windows file names
        fixedName = re.sub(forbiddenChars, '_', i_fileName)
        fileName = os.path.join(i_folder, fixedName)
        with open(fileName, 'w') as file:
            file.write(i_string)

        return fileName
    except Exception as e:
        ErrorLogging(f"Error in CreateNewTempCodeFile: {e}")


# Delete all temp.txt files in that folder
def CleanTempFiles():
    try:
        tempFiles = glob.glob(os.path.join(gs._FOLDER_TEMP, '*_TEMP.txt'))

        # Loop through the .txt files and delete them
        for file in tempFiles:
            os.remove(file)
    except Exception as e:
        ErrorLogging(f"Error in CleanTempFiles: {e}")