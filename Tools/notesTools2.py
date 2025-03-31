import Globals as gs
import re
from Tools.errorHandler import ErrorLogging
from WebsocketServer import SendWSMessage
import asyncio

# Check the content of a log and parse all data
def ParseContent(i_content, i_fileName, i_cursor):
    try: 
        # Variables
        codesArray = []                         # This is to store codes
        logLineRegex = re.compile(r"(^\d{4}\.\d{2}\.\d{2}\s+\d{2}\:\d{2}\:\d{2})\s+\w+\s+-\s+(.+)") # Regex to extract date and content
        lineMatch = []

        # Read line by line
        i_content.seek(i_cursor)                # Move the cursor to the last read position
        while True:
            line = i_content.readline()         # Let's read line by line
            if not line:                        # End of the document, out
                break

            lineMatch = logLineRegex.search(line)    # Process the line's content, 1st group of the regex is the date, 2nd is the content

            if lineMatch:
                # Variables
                foundPatternID = ''
                regexMatch = ''
                key = ''
                regex = ''

                for key, regex in gs.regexDict.items():             # Iterate the line with each regex
                    regexMatch = regex.search(lineMatch.groups()[1])
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
                                    dateTime = lineMatch.groups()[0]        # Date
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
                                gs.roundType = 'Special'
                            case "round_won":
                                gs.roundCondition = 'WIN'
                            case "round_lost":
                                gs.roundCondition = 'LOSE'
                                ResetRound()
                        
                        # Fix name of the round for the Decoder later
                        match gs.roundType:
                            case '8 Pages':
                                gs.roundType = '8pages'
                            
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
