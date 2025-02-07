from Tools.xmlTools import PopulateCodes, GetAllFiles, ReadCodeFiles
from Tools.fileTools import GetDateModified, GetModifiedFiles
import Globals as gs
from time import sleep

# The main loop that will connect to VRCs logs and check for codes
def CodesHunter():
    # Variables
    logFiles = []
    logFilesToCheck = []
    currentDateFiles = {}
    previousDateFiles = {}

    # Start the loop to watch all the files
    while True:
        # Let's retrieve all files again, just in case VRC crashed or was restarted, it creates a new log file
        logFiles = GetAllFiles(gs.configList['vrchat-log-path']+'output_log_*.txt')

        previousDateFiles = currentDateFiles                                              # Move the dates
        currentDateFiles = GetDateModified(logFiles)                                      # Obtain the new dates

        if currentDateFiles != previousDateFiles:
            print('Modified files detected, checking...')
            logFilesToCheck = GetModifiedFiles(currentDateFiles, previousDateFiles)      # Compare them and see what files we need to check

            PopulateCodes(  logFilesToCheck, 
                            gs.configList['keyword-start'],
                            gs.configList['keyword-end'],
                            gs.configList['keyword-date-end'],
                            gs.configList['codes-folder'])
        
        sleep( int(gs.configList['file-delay']) )                      # The program is very eepy, let it rest