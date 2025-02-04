from Tools.xmlTools import InitializeConfig, ReadCodeFiles
from Tools.fileTools import CreateFromDefault
from Tools.errorHandler import StartErrorHandler
from Tools.guiTools import CreateWindow, CreateTreeView
from CodesHunter import CodesHunter
import threading

'''
Author: MichelleDB - https://michelledb.com/
I have no direct relation with Terrors of Nowhere outside of being a fan and a Patreon supporter.

Terrors of Nowhere belongs to Beyond https://www.patreon.com/c/beyondVR

TODO:
- New field Notes
- Scrollbar
- Move initial config to a modal window
- Delete codes feature
- GUI polish
- Better exception handling
- Discord webhook

Outside dependencies:
Pyperclip: https://pypi.org/project/pyperclip/
'''

# Constants
_CONFIG_FILE = 'config.xml'
_VERSION = 'alpha 0.3.3'
_TITLE = f"ToN Codes {_VERSION} - by MichelleDB //// [Double click to copy]"
_HEIGHT = 620
_WIDTH = 300

# This is for the GUI
def RefreshCodes():
    return ReadCodeFiles(configList['codes-folder'])


if __name__ == "__main__":
    StartErrorHandler()

    CreateFromDefault(_CONFIG_FILE)                     # Verify the config file exist
    configList = InitializeConfig(_CONFIG_FILE)         # Retrieve all config data

    # The main program to check for codes and create the XML files
    mainThread = threading.Thread(target=CodesHunter, args=(configList,))
    mainThread.daemon = True
    mainThread.start()

    # GUI setup
    root = CreateWindow(_TITLE, _HEIGHT, _WIDTH)
    codesData = RefreshCodes()
    CreateTreeView(root, codesData, int(configList['gui-delay'])*1000, RefreshCodes)
    root.mainloop()
