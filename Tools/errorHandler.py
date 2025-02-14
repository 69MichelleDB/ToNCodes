import logging
import sys
import datetime
import os
import Globals as gs
from tkinter import messagebox

def ErrorLoging(i_exception):
    # Get the current date and time in the format YYYYMMDD_HHMMSS
    logFilename = os.path.join(gs._FOLDER_LOGS, datetime.datetime.now().strftime("logError_%Y%m%d_%H%M%S.txt"))

    # Set up logging with the dynamically generated filename (at the time of the error)
    logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=logFilename, 
                    filemode='a')  # a, for appending
    
    messagebox.showinfo("Error!", i_exception)
    logging.error(i_exception, exc_info=True)
