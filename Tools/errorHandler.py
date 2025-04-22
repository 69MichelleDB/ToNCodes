import logging
import sys
import datetime
import os
import Globals as gs
from tkinter import messagebox

def InitializeLoggers():
    gs.logger = logging.getLogger("Main logger")
    gs.logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    gs.loggerDebug = logging.FileHandler(os.path.join(gs._FOLDER_LOGS, "logDebug.txt"), mode="w")
    gs.loggerDebug.setLevel(logging.DEBUG)
    gs.loggerDebug.setFormatter(formatter)

    gs.loggerError = logging.FileHandler(os.path.join(gs._FOLDER_LOGS, "logError.txt"), mode="w")
    gs.loggerError.setLevel(logging.ERROR)
    gs.loggerError.setFormatter(formatter)

    gs.loggerInfo = logging.FileHandler(os.path.join(gs._FOLDER_LOGS, "logInfo.txt"), mode="w")
    gs.loggerInfo.setLevel(logging.INFO)
    gs.loggerInfo.setFormatter(formatter)

    gs.logger.addHandler(gs.loggerDebug)
    gs.logger.addHandler(gs.loggerError)
    gs.logger.addHandler(gs.loggerInfo)

    logging.getLogger("websockets").setLevel(logging.DEBUG)
    logging.getLogger("websockets").addHandler(gs.loggerDebug)


def ErrorLogging(i_exception, i_silent=False):
    # # Get the current date and time in the format YYYYMMDD_HHMMSS
    # logFilename = os.path.join(gs._FOLDER_LOGS, datetime.datetime.now().strftime("logError_%Y%m%d_%H%M%S.txt"))
    
    if i_silent == False:
        messagebox.showinfo("Error", f'{i_exception}\nMore information in the Log folder')
    gs.logger.error(i_exception+'\n\n', exc_info=True)