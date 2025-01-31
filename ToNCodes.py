from Tools.xmlTools import InitializeConfig, PopulateCodes, GetAllFiles
from Tools.fileTools import CreateFromDefault, GetDateModified, GetModifiedFiles
import time

'''
Current version alpha 0.2

Project started on 2025-01-30
Author: MichelleDB - https://michelledb.com/
I have no direct relation with Terrors of Nowhere outside of being a fan and a Patreon supporter.

Terrors of Nowhere belongs to Beyond https://www.patreon.com/c/beyondVR

TODO:
- Exception handling
- GUI, everything
- Discord webhook
'''

# Constants
_CONFIG_FILE = 'config.xml'

# Variables
_logFiles = []
_logFilesToCheck = []
_currentDateFiles = {}
_previousDateFiles = {}


# Main
if __name__ == "__main__":
    CreateFromDefault(_CONFIG_FILE)                     # Verify the config file exist
    configList = InitializeConfig(_CONFIG_FILE)         # Retrieve all config data
    
    # Start the loop to watch all the files
    while True:
        # Let's retrieve all files again, just in case VRC crashed or was restarted, it creates a new log file
        _logFiles = GetAllFiles(configList['vrchat-log-path']+'output_log_*.txt')

        _previousDateFiles = _currentDateFiles                                              # Move the dates
        _currentDateFiles = GetDateModified(_logFiles)                                      # Obtain the new dates

        if _currentDateFiles != _previousDateFiles:
            print('Modified files detected, checking...')
            _logFilesToCheck = GetModifiedFiles(_currentDateFiles, _previousDateFiles)      # Compare them and see what files we need to check

            PopulateCodes(  _logFilesToCheck, 
                            configList['keyword-start'],
                            configList['keyword-end'],
                            configList['keyword-date-end'],
                            configList['codes-folder'])
        
        time.sleep( int(configList['file-delay']) )                         # The program is very eepy, let it rest
