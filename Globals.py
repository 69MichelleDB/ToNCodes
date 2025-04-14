import os.path

# Constants
_VERSION = 'alpha-0.7.11'
_TITLE = f"ToNCodes {_VERSION} - by MichelleDB"
_GITHUB = 'https://github.com/69MichelleDB/ToNCodes'
_WSURL = "localhost"
_WSPORT = 11398
_URL = "app.tontrack.me"
_DEBUG_REFRESH = 200
_OSCURL = "127.0.0.1"
_PLS = 'pools.json'
_RX = 'regex.json'

# Main window
_WIDTH = 650
_HEIGHT = 300

# Manual Code window
_WIDTH_MC = 400
_HEIGHT_MC = 100

# Options window
_WIDTH_OPT = 640
_HEIGHT_OPT = 475

# About window
_WIDTH_ABOUT = 550
_HEIGHT_ABOUT = 360

# Debug window
_WIDTH_DEBUG = 500
_HEIGHT_DEBUG = 300

# OSC Param window
_WIDTH_OSCPARAM = 450
_HEIGHT_OSCPARAM = 500

# Folders
_FOLDER_CODES = 'Codes'
_FOLDER_LOGS = 'Logs'
_FOLDER_TEMPLATES = 'Templates'
_FOLDER_TEMP = 'Temp'
_FOLDER_TOOLS = 'Tools'
_FOLDER_TOOLS_ITEMS = 'Items'
_FOLDER_TOOLS_THEMES = 'Themes'
_FOLDER_TOOLS_THEMES_ASSETS = 'Assets'
_FOLDER_OSC= 'OSC'

# Files
_FILE_CONFIG = 'config.xml'
_FILE_CONTROLJSON = os.path.join(_FOLDER_CODES, 'control.json')
_FILE_FALLBACKOSCPROFILE = os.path.join(_FOLDER_TEMPLATES,_FOLDER_OSC,'ToNSM-Standard.json')
_FILE_POOLS = os.path.join(_FOLDER_TOOLS,_FOLDER_TOOLS_ITEMS,'pools.dat')
_FILE_SILLYNAMES = os.path.join(_FOLDER_TOOLS,_FOLDER_TOOLS_ITEMS,'silly.json')

# Global variables
titleMessage = ''
configList = {}
localeDict = {}
root = None
optionsRoot = None
TONStyles = {}
debugBarFrame = None
debugBarAfterID = None
writingFlag = False
wsFlag = False
newCodeAdded = True
forceRefreshCodes = False
pools = []
sillyNames = {}
regexDict = {}
codesData = []
fileBoxSelected = ''
fileBoxChanged = False
oscClient = None
oscJsonProfile = None
controlJson = {}
currentFile = ''

# Round and debugging variables
roundEvent = ''
roundNotJoined = -1
roundMap = ''
roundType = ''
roundKiller = ''
roundCondition = ''
lastWSMessage = ''
lastOSCMessage = ''

# TEMP
auxPathFirstBoot = None