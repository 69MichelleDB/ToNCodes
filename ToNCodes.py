from Tools.xmlTools import InitializeConfig, ReadCodeFiles, ModifyNode, VerifyConfigFields
from Tools.fileTools import VerifyInitFileStructure, VerifyConfigExists, CleanTempFiles, GetKillers
from Tools.guiTools import CreateWindow, HorizontalMenu, CreateTreeView, CalculatePosition
from Tools.errorHandler import ErrorLogging
from Tools.webhookTool import CheckForUpdates
from CodesHunter2 import CodesHunter2
import threading
import Globals as gs


'''
Author: MichelleDB - https://michelledb.com/
I have no direct relation with Terrors of Nowhere outside of being a fan and a Patreon supporter.

Terrors of Nowhere belongs to Beyond https://www.patreon.com/c/beyondVR

Outside dependencies:
Pyperclip: https://github.com/asweigart/pyperclip
screeninfo: https://github.com/rr-/screeninfo
cryptography: https://github.com/pyca/cryptography
requests: https://github.com/psf/requests
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

    # The main program to check for codes and create the XML files
    mainThread = threading.Thread(target=CodesHunter2)
    mainThread.daemon = True
    mainThread.start()

    # GUI setup
    gs.killersList = GetKillers()
    gs.root = CreateWindow(gs._TITLE + gs.titleMessage, gs._WIDTH, gs._HEIGHT, True)
    auxX,auxY = CalculatePosition(gs._WIDTH, gs._HEIGHT)
    gs.root.geometry(f'{gs._WIDTH}x{gs._HEIGHT}+{auxX}+{auxY}')
    HorizontalMenu(gs.root)
    codesData = RefreshCodes()
    CreateTreeView(gs.root, codesData, int(gs.configList['file-delay'])*1100, RefreshCodes)

    gs.root.mainloop()