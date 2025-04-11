from Tools.xmlTools import InitializeConfig, ReadCodeFiles, ModifyNode, VerifyConfigFields
from Tools.fileTools import VerifyInitFileStructure, VerifyConfigExists, CleanTempFiles, RegexCheck, PoolCheck, LoadLocale, LoadJson
from Tools.guiTools import CreateWindow, HorizontalMenu, HorizontalFileBox, CreateTreeView, CalculatePosition, ApplyStyle, DebugBar
from Tools.errorHandler import ErrorLogging
from Tools.netTools import CheckForUpdates, WSstart, InitializeOSCClient
from CodesHunter import CodesHunter
import threading
import Globals as gs


'''
ToN Codes: https://github.com/69MichelleDB/ToNCodes
Author: MichelleDB - https://michelledb.com/
I have no direct relation with Terrors of Nowhere outside of being a fan and a Patreon supporter.

Terrors of Nowhere belongs to Beyond https://www.patreon.com/c/beyondVR
tontrack.me by Cinossu: https://tontrack.me/
OSC standard naming by Kittenji: https://github.com/ChrisFeline/ToNSaveManager

Outside dependencies:
Pyperclip: https://github.com/asweigart/pyperclip
screeninfo: https://github.com/rr-/screeninfo
cryptography: https://github.com/pyca/cryptography
requests: https://github.com/psf/requests
websockets: https://github.com/python-websockets/websockets
python-osc: https://github.com/attwad/python-osc
vdf: https://github.com/ValvePython/vdf
'''


# This is for the GUI
def RefreshCodes():
    return ReadCodeFiles(gs._FOLDER_CODES)


if __name__ == "__main__":
    VerifyInitFileStructure()

    CleanTempFiles()                                                # Delete temp files from last session

    VerifyConfigExists(gs._FILE_CONFIG)                             # Verify the config file exist
    VerifyConfigFields(gs._FILE_CONFIG)
    gs.configList = InitializeConfig(gs._FILE_CONFIG)               # Retrieve all config data

    LoadLocale()
    CheckForUpdates()                                               # Check for new updates logic
    RegexCheck()

    # Websocket server
    if gs.configList['tontrack-ws'] == '1':
        secondThread = threading.Thread(target=WSstart)
        secondThread.daemon = True
        secondThread.start()

    # OSC Client
    InitializeOSCClient(gs.configList['osc-in-port'], gs.configList['osc-profile'])

    # The main program to check for codes and create the XML files
    mainThread = threading.Thread(target=CodesHunter)
    mainThread.daemon = True
    mainThread.start()

    # GUI setup
    gs.pools = PoolCheck()
    gs.sillyNames = LoadJson(gs._FILE_SILLYNAMES)
    
    gs.root = CreateWindow(gs._TITLE + gs.titleMessage, gs._WIDTH, gs._HEIGHT+30, True)
    auxX,auxY = CalculatePosition(gs._WIDTH, gs._HEIGHT)
    gs.root.geometry(f'{gs._WIDTH}x{gs._HEIGHT}+{auxX}+{auxY}')

    gs.codesData = RefreshCodes()

    HorizontalMenu(gs.root)
    HorizontalFileBox(gs.root)
    CreateTreeView(gs.root, int(gs.configList['ui-delay']), RefreshCodes)
    # Debug bar
    if gs.configList['debug-window'] == '1':
        DebugBar(gs.root)

    gs.root.mainloop()