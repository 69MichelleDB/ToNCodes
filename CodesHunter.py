import os.path
import Globals as gs
from time import sleep
from Tools.fileTools import ControlFile, LoadJson, SaveJson, CleanControlEntries, ControlFileUpdate, GetDateModified, GetModifiedFiles
from Tools.xmlTools import GetAllFiles, ReadControlFile, PopulateCodes2
from Tools.errorHandler import ErrorLogging


# The main loop that will connect to VRCs logs and check for codes
def CodesHunter():
    try:
        # Variables
        logFiles = []
        currentDateFiles = {}
        previousDateFiles = {}
        logFilesToCheck = []

        # Make sure the Control file exists
        gs.controlJson = ControlFile()
        
        # Clean the control file of non existent log files
        CleanControlEntries(gs.controlJson, GetAllFiles(gs.configList['vrchat-log-path']+'output_log_*.txt'))

        while True:
            # Let's retrieve all files again, just in case VRC crashed or was restarted, it creates a new log file
            logFiles = GetAllFiles(gs.configList['vrchat-log-path']+'output_log_*.txt')

            previousDateFiles = currentDateFiles                        # Move the old dates
            currentDateFiles = GetDateModified(logFiles)                # Obtain the new dates
            if gs.forceRefreshCodes:                                    # In case of a Code.xml file corruption this will force a refresh
                previousDateFiles = []
                gs.controlJson = ControlFile()                             # Refresh the control data to update the cursors
                gs.forceRefreshCodes = False
            if currentDateFiles != previousDateFiles:
                print('Modified files detected, checking...')
                logFilesToCheck = GetModifiedFiles(currentDateFiles, previousDateFiles)             # Compare them and see what files we need to check
                logFilesToCheckSorted = sorted(logFilesToCheck, key=lambda x: x[0])                 # If we don't sort, on first boot we risk a mess
                logFilesToCheckCursor = []
                
                for log in logFilesToCheckSorted:
                    cursorOld = '0'
                    if log[0] in gs.controlJson:
                        cursorOld = gs.controlJson[log[0]]["cursor"]

                    cursorAux = PopulateCodes2(log[0], gs._FOLDER_CODES, cursorOld)
                    ControlFileUpdate(gs.controlJson, log[0], log[1], cursorAux)
                    SaveJson(gs._FILE_CONTROLJSON, gs.controlJson)
                    print('Updated Control file')

            sleep( float(gs.configList['file-delay']) )                      # The program is very eepy, let it rest
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CodesHunter: {e}")
