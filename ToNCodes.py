from Tools.xmlTools import InitializeConfig, ReadCodeFiles, ModifyNode, VerifyConfigFields
from Tools.fileTools import VerifyInitFileStructure, VerifyConfigExists, CleanTempFiles, GetKeyData, RegexCheck
from Tools.guiTools import CreateWindow, HorizontalMenu, CreateTreeView, CalculatePosition
from Tools.errorHandler import ErrorLogging
from Tools.webhookTool import CheckForUpdates
from CodesHunter2 import CodesHunter2
import threading
import Globals as gs
from WebsocketServer import WSstart


'''
ToN Codes: https://github.com/69MichelleDB/ToNCodes
Author: MichelleDB - https://michelledb.com/
I have no direct relation with Terrors of Nowhere outside of being a fan and a Patreon supporter.

Terrors of Nowhere belongs to Beyond https://www.patreon.com/c/beyondVR
tontrack.me by Cinossu: https://tontrack.me/

Outside dependencies:
Pyperclip: https://github.com/asweigart/pyperclip
screeninfo: https://github.com/rr-/screeninfo
cryptography: https://github.com/pyca/cryptography
requests: https://github.com/psf/requests
websockets: https://github.com/python-websockets/websockets
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

    CheckForUpdates()                                               # Check for new updates logic

    RegexCheck()

    # Websocket server
    if gs.configList['tontrack-ws'] == '1':
        secondThread = threading.Thread(target=WSstart)
        secondThread.daemon = True
        secondThread.start()

    # The main program to check for codes and create the XML files
    mainThread = threading.Thread(target=CodesHunter2)
    mainThread.daemon = True
    mainThread.start()

    # GUI setup
    gs.killersList = GetKeyData(gs._FILE_DATAK, gs._FILE_DATA, 'K')
    gs.unboundsDict = GetKeyData(gs._FILE_DATAUK, gs._FILE_DATAU, 'U')
    
    gs.root = CreateWindow(gs._TITLE + gs.titleMessage, gs._WIDTH, gs._HEIGHT, True)
    auxX,auxY = CalculatePosition(gs._WIDTH, gs._HEIGHT)
    gs.root.geometry(f'{gs._WIDTH}x{gs._HEIGHT}+{auxX}+{auxY}')
    HorizontalMenu(gs.root)
    codesData = RefreshCodes()
    CreateTreeView(gs.root, codesData, int(gs.configList['file-delay'])*1000, RefreshCodes)

    gs.root.mainloop()