from Tools.xmlTools import PopulateCodes, GetAllFiles, ReadCodeFiles
from Tools.fileTools import GetDateModified, GetModifiedFiles
from time import sleep

# The main loop that will connect to VRCs logs and check for codes
def CodesHunter(configList):
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