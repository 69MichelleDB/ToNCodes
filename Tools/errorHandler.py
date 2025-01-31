import logging
import sys
import datetime
import os

# Set up logging
def show_error_popup(i_excType, i_excValue, i_excTraceback):
    # Ignore KeyboardInterrupt to allow for a clean exit
    if issubclass(i_excType, KeyboardInterrupt):
        sys.__excepthook__(i_excType, i_excValue, i_excTraceback)
        return

    # Get the current date and time in the format YYYYMMDD_HHMMSS
    logFilename = os.path.join('Logs', datetime.datetime.now().strftime("logError_%Y%m%d_%H%M%S.txt"))

    # Set up logging with the dynamically generated filename (at the time of the error)
    logging.basicConfig(filename=logFilename, level=logging.ERROR, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Log the error
    logging.error("Uncaught exception", exc_info=(i_excType, i_excValue, i_excTraceback))
 
    print("ToNCodes - Error", f"An unexpected error occurred:\n{i_excValue}")


# Override the default exception handler
def StartErrorHandler():
    sys.excepthook = show_error_popup