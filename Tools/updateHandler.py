import Tools.xmlTools
import Globals as gs


def WarningHandler(i_result):
    if i_result != 0:
        if i_result == 1:           # In case the user was warned about the update, don't bother them anymore
            Tools.xmlTools.ModifyNode(gs._FILE_CONFIG, 'check-updates-warned', '1')
        elif i_result == 2:          # The user has the latest update, reset the warning in case there's a new future update
            Tools.xmlTools.ModifyNode(gs._FILE_CONFIG, 'check-updates-warned', '0')
        
        if i_result == 1 or i_result == 3:
            gs.titleMessage = gs.localeDict['Update-New-Title']