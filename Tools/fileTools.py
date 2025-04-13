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
import vdf
import Tools.Items.Encounters as agent
import requests
from Tools.middlePass import ModifyNode_Call

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

# Reset config file
def ResetConfigFile():
    try:
        os.remove(gs._FILE_CONFIG)
        VerifyConfigExists(gs._FILE_CONFIG)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ResetConfigFile: {e}")

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
def GetPossibleVRCPath2():
    try:
        result = ''
        vrchatID = '438100'

        print(f'Platform: {platform.system()}')
        userName = getpass.getuser()
        print(f'User name: {userName}')
      
        if platform.system() == "Windows":
            result = f'c:\\users\\{userName}\\AppData\\LocalLow\\VRChat\\VRChat\\'
        elif platform.system() == "Linux":
            possiblePaths = [
                            f'/home/{userName}/.steam/debian-installation/steamapps/libraryfolders.vdf',
                            f'/home/{userName}/.local/share/Steam/steamapps/libraryfolders.vdf',
                            f'/home/{userName}/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/libraryfolders.vdf'
                            ]
            for libraryfoldersFile in possiblePaths:
                if os.path.exists(libraryfoldersFile):
                    print(f'Found steam path: {libraryfoldersFile}')
                    vdfFile = {}
                    with open(libraryfoldersFile, 'r') as file:         # This vdf file has the path to all games, we can pinpoint where vrc logs might be
                        vdfFile = vdf.loads(file.read())
                    for key in vdfFile['libraryfolders']:
                        if vrchatID in vdfFile['libraryfolders'][key]['apps']:
                            checkThisPath = os.path.join(vdfFile['libraryfolders'][key]['path'], f"steamapps/compatdata/{vrchatID}/pfx/drive_c/users/steamuser/AppData/LocalLow/VRChat/VRChat/")
                            if os.path.exists(checkThisPath):
                                result = checkThisPath
                                break
        else:
            print('Might be something else')

        return result
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in GetPossibleVRCPath2: {e}")


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

# Check if the Control file (we'll store file, mod. date and cursor position here) exists and loads it
def ControlFile():
    try:
        # Make sure the Control file exists
        if not os.path.exists(gs._FILE_CONTROLJSON):
            with open(gs._FILE_CONTROLJSON, 'w') as file:
                file.write('{}')
        return LoadJson(gs._FILE_CONTROLJSON)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ControlFile: {e}")

# Loop the json and if there's a file that doesn't exist anymore, delete it from control
def CleanControlEntries(i_controlJson, i_logFiles):
    try: 
        dictCopy = i_controlJson.copy()     # If we delete entries from i_controlJson the for will throw an exception, I'll iterate a copy
        print('Checking for old entries in Control file...')
        for entry in dictCopy:
            if entry not in i_logFiles:
                print(f"{entry} doesn't exist anymore, deleting entry from control file.") 
                del i_controlJson[entry]
        SaveJson(gs._FILE_CONTROLJSON, i_controlJson)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CleanControlEntries: {e}")

# Try to update an entry in the control file, if there's no entry, insert a new entry
def ControlFileUpdate(i_controlFile, i_file, i_date, i_cursor):
    try:
        if i_file in i_controlFile:
            i_controlFile[i_file]["date"] = i_date
            i_controlFile[i_file]["cursor"] = i_cursor
        else:
            i_controlFile[i_file] = {
                "date" : i_date,
                "cursor" : i_cursor
            }
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ModifyCode: {e}")

def RegexCheck():
    try:
        response = requests.get(f"https://{gs._URL}/{gs._RX}")
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

def PoolCheck():
    try:
        result = []
        jsonFile = {}
        ver = ''
        rx = re.compile(r"\s+\w+\.TON_BUILDTS\s+=\s+(\d+);")
        response = requests.get(f"https://{gs._URL}/")

        if response.status_code == 200:
            matched = rx.search(response.text)
            ver = matched.groups()[0] if matched else ''
        else:
            print("Couldn't connect")

        if gs.configList['pool-ver'] != ver or not os.path.exists(gs._FILE_POOLS):
            response = None
            response = requests.get(f"https://{gs._URL}/{gs._PLS}?v={ver}")
            jsonFile = response.json()
            gs.configList['pool-key'] = Fernet.generate_key()
            ModifyNode_Call(gs._FILE_CONFIG, 'pool-key', gs.configList['pool-key'].decode('utf-8'))
            cipher = Fernet(gs.configList['pool-key'])
            with open(gs._FILE_POOLS, 'wb') as file:
                file.write(cipher.encrypt(json.dumps(jsonFile).encode('utf-8')))
            gs.configList['pool-ver'] = ver
            ModifyNode_Call(gs._FILE_CONFIG, 'pool-ver', gs.configList['pool-ver'])
        else:
            cipher = Fernet(gs.configList['pool-key'].encode('utf-8'))
            with open(gs._FILE_POOLS, 'r') as file:
                jsonFile = json.loads(cipher.decrypt(file.read()).decode('utf-8'))

        if len(jsonFile)>0:
            for conceptList in jsonFile:
                if conceptList in ['locations','achievements','tester_achievements']:
                    break
                for itemList in jsonFile[conceptList]:
                    result.append( agent.Encounters(conceptList, itemList['id'], itemList['value'], itemList['name'], itemList['variant_type'] if 'variant_type' in itemList else None) )
        else:
            messagebox.showerror(gs.localeDict['Error-Pools-Head'],gs.localeDict['Error-Pools-Body'].format(url=gs._GITHUB))
        
        return result
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in PoolCheck: {e}")

# Simple function to load json files data
def LoadJson(i_path):
    try:
        with open(i_path, 'r') as file:
            return json.loads(file.read())
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in LoadJson: {e}")

def SaveJson(i_path, i_jsonDict):
    try: 
        with open(i_path, 'w') as file:
            json.dump(i_jsonDict, file, indent=4)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in SaveJson: {e}")

# Load the selected locale in the global dict
def LoadLocale():
    try:
        print(f"Loading locale {gs.configList['locale']}")
        gs.localeDict = LoadJson(os.path.join("Tools","Locale",f"{gs.configList['locale']}.json"))
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in LoadLocale: {e}")
        

# Obtain all files from a given directory
def GetAllFiles(i_path, i_file='*', i_absolutePath=False):
    try:
        result = []
        for file in glob.glob(os.path.join(*i_path, i_file)):
            if not i_absolutePath:
                result.append(file.replace(str(os.path.join(*i_path)) + os.sep, ''))
            else:
                result.append(file)
        return result
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in GetAllThemes: {e}")