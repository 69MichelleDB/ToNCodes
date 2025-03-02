import os.path
import Globals as gs
from time import sleep
from Tools.fileTools import ControlFile, GetDateModified, GetModifiedFiles
from Tools.xmlTools import GetAllFiles, ReadControlFile, PopulateCodes2, ControlFileUpdate, CleanControlEntries
from Tools.errorHandler import ErrorLogging


# The main loop that will connect to VRCs logs and check for codes
def CodesHunter2():
    try:
        # Variables
        logFiles = []
        currentDateFiles = {}
        previousDateFiles = {}
        controlData = []
        logFilesToCheck = []
        
        # Make sure the Control file exists
        controlFile = ControlFile()
        
        # Clean the control file of non existent log files
        CleanControlEntries(controlFile, GetAllFiles(gs.configList['vrchat-log-path']+'output_log_*.txt'))

        # Initialize with control file's dates
        controlData = ReadControlFile(controlFile)
        for item in controlData:
            currentDateFiles[item[0]] = item[1]                         # 0 File, 1 Date

        while True:
            # Let's retrieve all files again, just in case VRC crashed or was restarted, it creates a new log file
            logFiles = GetAllFiles(gs.configList['vrchat-log-path']+'output_log_*.txt')

            previousDateFiles = currentDateFiles                        # Move the old dates
            currentDateFiles = GetDateModified(logFiles)                # Obtain the new dates
            if gs.forceRefreshCodes:                                    # In case of a Code.xml file corruption this will force a refresh
                previousDateFiles = []
                controlData = ReadControlFile(controlFile)              # Refresh the control data to update the cursors
                gs.forceRefreshCodes = False
            if currentDateFiles != previousDateFiles:
                print('Modified files detected, checking...')
                logFilesToCheck = GetModifiedFiles(currentDateFiles, previousDateFiles)             # Compare them and see what files we need to check
                logFilesToCheckSorted = sorted(logFilesToCheck, key=lambda x: x[0])                 # If we don't sort, on first boot we risk a mess
                logFilesToCheckCursor = []
                
                for log in logFilesToCheckSorted:
                    cursorOld = '0'
                    for item in controlData:
                        if item[0]==log[0]:
                            cursorOld = item[2]
                            break
                    cursorAux = PopulateCodes2(log[0], gs._FOLDER_CODES, cursorOld)
                    ControlFileUpdate(controlFile, log[0], log[1], cursorAux)
                    controlData = ReadControlFile(controlFile)
                    print('Updated Control file')

            sleep( float(gs.configList['file-delay']) )                      # The program is very eepy, let it rest
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CodesHunter2: {e}")
