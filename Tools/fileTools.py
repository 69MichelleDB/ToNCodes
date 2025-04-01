import os
import sys
import platform
import getpass
import glob
import Globals as gs
import re
from tkinter import messagebox
from Tools.errorHandler import ErrorLogging
from cryptography.fernet import Fernet
import json
import Tools.Items.Killer as agent
import requests

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
        if os.path.exists(gs._FILE_CONFIG) == False:                # Check if there's a config file, if there's none, if the template is there
            if os.path.exists(os.path.join(gs._FOLDER_TEMPLATES,f'{gs._FILE_CONFIG}.default')) == False:
                messagebox.showwarning("Warning", "Templates/config.xml.default not found, please verify your installation")
                sys.exit()
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in VerifyInitFileStructure: {e}")
    

# To avoid uploading my config files we'll have .defaults and just duplicate them if they don't exist
def VerifyConfigExists(i_file):
    try:
        if not os.path.exists(i_file):                    # If the file doesn't exist, duplicate the template
            print(f'The {os.path.basename(i_file)} file does not exist, creating...')
            defaultConfigFile = os.path.join(gs._FOLDER_TEMPLATES, i_file+'.default')
            if os.path.exists(defaultConfigFile):
                with open(defaultConfigFile, 'r') as src, open(i_file, 'w') as dst:
                    dst.write(src.read())
            else:
                raise FileNotFoundError(f"Default template file '{defaultConfigFile}' not found.")
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CreateFromDefault: {e}")


# Pass it a list of files and obtain a dictionary with the file name and the date modified
def GetDateModified(i_files):
    try:
        filesDict = {}    
        for file in i_files:
            filesDict[file] = str(os.path.getmtime(file))

        return filesDict
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in GetDateModified: {e}")


# Pass it a pair of dictionaries with current an previous dates, return only the ones we need to check
def GetModifiedFiles(i_currentDates, i_previousDates):
    try:
        filesToCheck = []    
        for file in i_currentDates:
            if file not in i_previousDates or i_currentDates[file] != i_previousDates[file]:    # if the file is new or if the date has changed
                filesToCheck.append((file, i_currentDates[file]))
                print(f'{os.path.basename(file)} was modified({i_currentDates[file]}), adding to list')

        return filesToCheck
    except Exception as e:
        print(e)
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
        print(e)
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
        print(e)
        ErrorLogging(f"Error in CreateNewTempCodeFile: {e}")


# Delete all temp.txt files in that folder
def CleanTempFiles():
    try:
        tempFiles = glob.glob(os.path.join(gs._FOLDER_TEMP, '*_TEMP.txt'))

        # Loop through the .txt files and delete them
        for file in tempFiles:
            os.remove(file)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CleanTempFiles: {e}")

# Check if the Control file (we'll store file, mod. date and cursor position here) exists and returns the full path
def ControlFile():
    try:
        # Make sure the Control file exists
        filePath = os.path.join(gs.configList['codes-folder'], gs._FILE_CONTROL)
        if not os.path.exists(filePath):
            with open(filePath, 'w') as file:
                file.write('<?xml version="1.0" ?><Root></Root>')

        return filePath
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ControlFile: {e}")


# If you're reading this and trying to datamine killer's info I'm not gonna stop you, this is just so it's not in plain text
def GetKeyData(i_key, i_data, i_type):
    result = None

    with open(i_key, 'r') as file:     
        key = file.read()

    cipher = Fernet(key)

    with open(i_data, 'r') as file:
        data = file.read()

    match i_type:
        case 'K':
            result = []
            killerList = json.loads(cipher.decrypt(data).decode('utf-8'))

            for typeList in killerList:
                #print(typeList)
                for killers in killerList[typeList]:
                    #print(f'{killers['id']},{killers['value']},{killers['name']}')
                    result.append( agent.Killer(typeList, killers['id'], killers['value'], killers['name']) )
        case 'U':
            result = {}
            result = json.loads(cipher.decrypt(data).decode('utf-8'))

    return result

def RegexCheck():
    try:
        response = requests.get(gs._RX)
        if response.status_code == 200:
            gs.regexDict = response.json()
            for key, pattern in gs.regexDict.items():       
                gs.regexDict[key] = re.compile(pattern)                     # Convert to a compiled regex pattern
            gs.regexDict["TONCODE"]=re.compile(r"^\[START\](.*)\[END\]$")   # Custom regexes
            #gs.regexDict["TONPLAYERNAME"]=re.compile(r"^User Authenticated: (\S+)\s\((usr_[a-z0-9\-]+)\)$")    # I noticed a log that had a code after a OnPlayerLeft <player>, keep in case this needs revisitng
            gs.regexDict["TONWINTER"]=re.compile(r"^winter!$")
            gs.regexDict["TONWAPRIL"]=re.compile(r"^silly!$")
            print("Regex loaded")
        else:
            print(f"Failed to retrieve regex data. Status code: {response.status_code}")
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in RegexCheck: {e}")

# Load the selected locale in the global dict
def LoadLocale():
    try:
        print(f"Loading locale {gs.configList['locale']}")
        with open(os.path.join("Tools","Locale",f"{gs.configList['locale']}.json"), 'r') as file:
            gs.localeDict = json.loads(file.read())
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in LoadLocale: {e}")