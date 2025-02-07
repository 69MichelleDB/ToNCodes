from Tools.xmlTools import InitializeConfig, ReadCodeFiles
from Tools.fileTools import CreateFromDefault
from Tools.errorHandler import StartErrorHandler
from Tools.guiTools import CreateWindow, HorizontalMenu, CreateTreeView, CreateOptionsWindow
from CodesHunter import CodesHunter
import threading
import Globals as gs

'''
Author: MichelleDB - https://michelledb.com/
I have no direct relation with Terrors of Nowhere outside of being a fan and a Patreon supporter.

Terrors of Nowhere belongs to Beyond https://www.patreon.com/c/beyondVR

TODO:
- New field Notes
- Delete codes feature
- GUI polish
- Better exception handling
- Discord webhook

Outside dependencies:
Pyperclip: https://pypi.org/project/pyperclip/
'''



# This is for the GUI
def RefreshCodes():
    return ReadCodeFiles(gs.configList['codes-folder'])


if __name__ == "__main__":
    StartErrorHandler()

    CreateFromDefault(gs._CONFIG_FILE)                             # Verify the config file exist
    gs.configList = InitializeConfig(gs._CONFIG_FILE)              # Retrieve all config data

    # The main program to check for codes and create the XML files
    mainThread = threading.Thread(target=CodesHunter)
    mainThread.daemon = True
    mainThread.start()

    # GUI setup
    gs.root = CreateWindow(gs._TITLE, gs._HEIGHT, gs._WIDTH, True)
    HorizontalMenu(gs.root)
    codesData = RefreshCodes()
    CreateTreeView(gs.root, codesData, int(gs.configList['gui-delay'])*1000, RefreshCodes)

    gs.root.mainloop()
