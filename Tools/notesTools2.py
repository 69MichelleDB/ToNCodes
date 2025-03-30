import Globals as gs
import re
from Tools.errorHandler import ErrorLogging
from WebsocketServer import SendWSMessage
import asyncio

# Check the content of a log and parse all data
def ParseContent(i_content, i_fileName, i_cursor):
    try: 
        # Variables
        logHeaderStr = "-  "                    # This is to remove VRC's date and meta
        logHeaderDebugStr = " Debug"            # This is to obtain VRC's date for the code
        codesArray = []                         # This is to store codes

        # Read line by line

        i_content.seek(i_cursor)    # Move the cursor to the last read position
        while True:
            ogLine = i_content.readline()       # Let's read line by line
            if not ogLine:                      # End of the document, out
                break
            else:
                line = ogLine                                   # We will need the date for the codes
                cursorLine = line.find(logHeaderStr)            # Remove VRC's date and meta
                line = line[cursorLine + len(logHeaderStr):]

            # Process the line's content

            # Variables
            foundPatternID = ''
            regexMatch = ''
            key = ''
            regex = ''

            for key, regex in gs.regexDict.items():             # Iterate the line with each regex
                regexMatch = regex.search(line)
                if regexMatch:
                    groups = regexMatch.groups()                # Extract each value from the regex
                    args = []
                    for i, value in enumerate(groups):
                        args.append(value)
                    match key:                                      # Process depending on what we got
                        case "TONWINTER":                           
                            gs.roundEvent = "Winterfest"
                        case "TONWAPRIL":                           
                            gs.roundEvent = "AprilFools"
                        case "TONCODE":                             # Process the code
                            print("Code found!")
                            if gs.roundCondition != '':
                                newCode = args[0]                       # Code
                                ogLine.find(logHeaderDebugStr)
                                dateTime = ogLine[:cursorLine]          # Date
                                note = gs.roundCondition if gs.roundCondition == 'RESPAWN' else f"{gs.roundMap}, {gs.roundType}, {gs.roundKiller}, {gs.roundEvent}"
                                codesArray.append((i_fileName, dateTime, newCode, note))
                            else:
                                print("There was no round condition, code wasn't saved.")
                            ResetRound()
                        case "opt_in":                              # Player joins the game
                            gs.roundNotJoined = 1
                        case "opt_out":                             # Opting out means they respawned
                            gs.roundNotJoined = -1
                            gs.roundCondition = 'RESPAWN'
                        case "round_map":
                            gs.roundMap = f"{args[0]} ({args[1]})"
                            gs.roundType = args[2]
                        case "round_killers":
                            gs.roundKiller = f"{args[0]} {args[1]} {args[2]}"
                            gs.roundType = args[3]
                        case "is_gigabyte":
                            gs.roundType = 'Gigabytes'
                        case "round_won":
                            gs.roundCondition = 'WIN'
                        case "round_lost":
                            gs.roundCondition = 'LOSE'
                            ResetRound()
                    # # Special rounds
                    # I'll review these as I encounter them in game to see how I'll handle them for the notes, probably unify gigabyte and neo pilot
                    # if key in ["is_meatball_man","is_hungry_home_invader", \
                    #     "is_wild_yet_bloodthirsty_creature","is_glorbo","is_atrached", \
                    #     "is_neo_pilot", \
                    #     "is_foxy","is_gigabyte"]:
                    #     gs.roundSpecialKiller = key
                        
                    if key not in ['TONWINTER','TONWAPRIL','TONCODE']:
                        SendWSMessage(key, args)
                    break
            
        cursor = i_content.tell()                               # If we are done, recover where the cursor is, which should be at the end
        return cursor, codesArray
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ParseContent: {e}")

# Reset all Round variables
def ResetRound():
    gs.roundMap = ''
    gs.roundType = ''
    gs.roundKiller = ''
    gs.roundCondition = ''
    gs.roundNotJoined = -1
    gs.roundSpecialKiller = ''
