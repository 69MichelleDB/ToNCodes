import os.path

# Constants
_VERSION = 'alpha-0.7.1'
_TITLE = f"ToNCodes {_VERSION} - by MichelleDB"
_GITHUB = 'https://github.com/69MichelleDB/ToNCodes'
_WSURL = "localhost"
_WSPORT = 11398
_RX = "https://app.tontrack.me/regex.json"

# Main window
_WIDTH = 770
_HEIGHT = 300

# Manual Code window
_WIDTH_MC = 400
_HEIGHT_MC = 100

# Options window
_WIDTH_OPT = 600
_HEIGHT_OPT = 220

# About window
_WIDTH_ABOUT = 550
_HEIGHT_ABOUT = 265

# Debug window
_WIDTH_DEBUG = 500
_HEIGHT_DEBUG = 300

# Folders
_FOLDER_CODES = 'Codes'
_FOLDER_LOGS = 'Logs'
_FOLDER_TEMPLATES = 'Templates'
_FOLDER_TEMP = 'Temp'

# Files
_FILE_CONFIG = 'config.xml'
_FILE_CONTROL = 'control.xml'
_FILE_DATA = os.path.join('Tools','Items','data')
_FILE_DATAK = os.path.join('Tools','Items','datak')
_FILE_DATASILLY = os.path.join('Tools','Items','data_silly')
_FILE_DATAKSILLY = os.path.join('Tools','Items','datak_silly')
_FILE_DATAU = os.path.join('Tools','Items','datau')
_FILE_DATAUK = os.path.join('Tools','Items','datauk')

# Global variables
configList = {}
root = None
debugRoot = None
titleMessage = ''
writingFlag = False
wsFlag = False
newCodeAdded = True
forceRefreshCodes = False
killersList = []
killersListSilly = []
killersListCurrent = []
unboundsDict = {}
regexDict = {}

# Round variables
roundEvent = ''
roundNotJoined = -1
roundMap = ''
roundType = ''
roundKiller = ''
roundSpecialKiller = ''
roundCondition = ''

# TEMP
auxPathFirstBoot = None