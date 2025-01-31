from Tools.xmlTools import InitializeConfig, PopulateCodes, GetAllFiles
from Tools.fileTools import CreateFromDefault, GetDateModified, GetModifiedFiles
from Tools.errorHandler import StartErrorHandler
from time import sleep
import threading

'''
Current version alpha 0.2.1

Project started on 2025-01-30
Author: MichelleDB - https://michelledb.com/
I have no direct relation with Terrors of Nowhere outside of being a fan and a Patreon supporter.

Terrors of Nowhere belongs to Beyond https://www.patreon.com/c/beyondVR

TODO:
- Better exception handling
- GUI, everything
- Discord webhook
'''

# Constants
_CONFIG_FILE = 'config.xml'


# The main loop that will connect to VRCs log and check for codes
def CodesHunter():
    # Variables
    logFiles = []
    logFilesToCheck = []
    currentDateFiles = {}
    previousDateFiles = {}

    # Start the loop to watch all the files
    while True:
        # Let's retrieve all files again, just in case VRC crashed or was restarted, it creates a new log file
        logFiles = GetAllFiles(configList['vrchat-log-path']+'output_log_*.txt')

        previousDateFiles = currentDateFiles                                              # Move the dates
        currentDateFiles = GetDateModified(logFiles)                                      # Obtain the new dates

        if currentDateFiles != previousDateFiles:
            print('Modified files detected, checking...')
            logFilesToCheck = GetModifiedFiles(currentDateFiles, previousDateFiles)      # Compare them and see what files we need to check

            PopulateCodes(  logFilesToCheck, 
                            configList['keyword-start'],
                            configList['keyword-end'],
                            configList['keyword-date-end'],
                            configList['codes-folder'])
        
        sleep( int(configList['file-delay']) )                      # The program is very eepy, let it rest



if __name__ == "__main__":
    StartErrorHandler()

    CreateFromDefault(_CONFIG_FILE)                     # Verify the config file exist
    configList = InitializeConfig(_CONFIG_FILE)         # Retrieve all config data

    mainThread = threading.Thread(target=CodesHunter)
    mainThread.daemon = True
    mainThread.start()

    # Keep main running
    while True:
        sleep(1)