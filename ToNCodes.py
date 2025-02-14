from Tools.xmlTools import InitializeConfig, ReadCodeFiles, ModifyNode
from Tools.fileTools import VerifyInitFileStructure, CreateFromDefault, CleanTempFiles
from Tools.guiTools import CreateWindow, HorizontalMenu, CreateTreeView, CalculatePosition
from Tools.errorHandler import ErrorLogging
from Tools.webhookTool import CheckForUpdates
from CodesHunter import CodesHunter
import threading
import Globals as gs


'''
Author: MichelleDB - https://michelledb.com/
I have no direct relation with Terrors of Nowhere outside of being a fan and a Patreon supporter.

Terrors of Nowhere belongs to Beyond https://www.patreon.com/c/beyondVR

Outside dependencies:
Pyperclip: https://github.com/asweigart/pyperclip
screeninfo: https://github.com/rr-/screeninfo
'''


# This is for the GUI
def RefreshCodes():
    return ReadCodeFiles(gs._FOLDER_CODES)


if __name__ == "__main__":
    VerifyInitFileStructure()

    CleanTempFiles()

    CreateFromDefault(gs._CONFIG_FILE)                              # Verify the config file exist
    gs.configList = InitializeConfig(gs._CONFIG_FILE)               # Retrieve all config data

    CheckForUpdates()                                               # Check for new updates logic

    # The main program to check for codes and create the XML files
    mainThread = threading.Thread(target=CodesHunter)
    mainThread.daemon = True
    mainThread.start()

    # GUI setup
    gs.root = CreateWindow(gs._TITLE + gs.titleMessage, gs._WIDTH, gs._HEIGHT, True)
    auxX,auxY = CalculatePosition(gs._WIDTH, gs._HEIGHT)
    gs.root.geometry(f'{gs._WIDTH}x{gs._HEIGHT}+{auxX}+{auxY}')
    HorizontalMenu(gs.root)
    codesData = RefreshCodes()
    CreateTreeView(gs.root, codesData, int(gs.configList['gui-delay'])*1000, RefreshCodes)

    gs.root.mainloop()
