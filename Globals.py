import os.path

# Constants
_VERSION = 'alpha-0.7.4'
_TITLE = f"ToNCodes {_VERSION} - by MichelleDB"
_GITHUB = 'https://github.com/69MichelleDB/ToNCodes'
_WSURL = "localhost"
_WSPORT = 11398
_RX = "https://app.tontrack.me/regex.json"

# Main window
_WIDTH = 650
_HEIGHT = 300

# Manual Code window
_WIDTH_MC = 400
_HEIGHT_MC = 100

# Options window
_WIDTH_OPT = 610
_HEIGHT_OPT = 275

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
_FOLDER_TOOLS = 'Tools'
_FOLDER_TOOLS_ITEMS = 'Items'
_FOLDER_TOOLS_THEMES = 'Themes'
_FOLDER_TOOLS_THEMES_ASSETS = 'Assets'

# Files
_FILE_CONFIG = 'config.xml'
_FILE_CONTROL = 'control.xml'
_FILE_DATA = os.path.join(_FOLDER_TOOLS,_FOLDER_TOOLS_ITEMS,'data')
_FILE_DATAK = os.path.join(_FOLDER_TOOLS,_FOLDER_TOOLS_ITEMS,'datak')
_FILE_DATASILLY = os.path.join(_FOLDER_TOOLS,_FOLDER_TOOLS_ITEMS,'data_silly')
_FILE_DATAKSILLY = os.path.join(_FOLDER_TOOLS,_FOLDER_TOOLS_ITEMS,'datak_silly')
_FILE_DATAU = os.path.join(_FOLDER_TOOLS,_FOLDER_TOOLS_ITEMS,'datau')
_FILE_DATAUK = os.path.join(_FOLDER_TOOLS,_FOLDER_TOOLS_ITEMS,'datauk')

# Global variables
configList = {}
localeDict = {}
root = None
TONStyles = {}
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
codesData = []
fileBoxSelected = ''
fileBoxChanged = False

# Round variables
roundEvent = ''
roundNotJoined = -1
roundMap = ''
roundType = ''
roundKiller = ''
roundCondition = ''

# TEMP
auxPathFirstBoot = None