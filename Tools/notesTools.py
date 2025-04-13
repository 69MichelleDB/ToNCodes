import Globals as gs
import re
from Tools.errorHandler import ErrorLogging
from Tools.netTools import SendWSMessage, OSCOrder, ExecuteOSCList, SendOSCMessage, ResetRoundOSC, NewRound
from Tools.Items.Encounters import TerrorID8Pages
import asyncio

# Check the content of a log and parse all data
def ParseContent(i_content, i_fileName, i_cursor):
    try: 
        # Variables
        codesArray = []                         # This is to store codes
        logLineRegex = re.compile(r"(^\d{4}\.\d{2}\.\d{2}\s+\d{2}\:\d{2}\:\d{2})\s+\w+\s+-\s+(.+$)") # Regex to extract date and content
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

                OSCorderList = []

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
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values']))
                            case "opt_out":                             # Opting out means they respawned
                                gs.roundNotJoined = -1
                                gs.roundCondition = 'RESPAWN'
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values'], 'resetRound'))
                            case "round_start":
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values'], 'newRound'))
                            case "round_map":
                                gs.roundMap = f"{args[0]} ({args[1]})"
                                gs.roundType = args[2]
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], args[1]))
                                OSCorderList.append(OSCOrder('round_type', gs.oscJsonProfile['round_type']['variable'], gs.oscJsonProfile['round_type']['values'][args[2]]))
                            case "round_map_swap":
                                print('round_map_swap placeholder, I need an example to see how the map is fed, is name and id or just name?') # TODO
                            case "round_killers":
                                if args[3] != '':       # I found a case with an 8 pages where the game returned an empty round with other killers before the round ended
                                    gs.roundKiller = f"{args[0]} {args[1]} {args[2]}"
                                    gs.roundType = args[3]
                                    if args[3] != '8 Pages':
                                        OSCorderList.append(OSCOrder('round_killer1', gs.oscJsonProfile['round_killer1']['variable'], int(args[0])))
                                        OSCorderList.append(OSCOrder('round_killer2', gs.oscJsonProfile['round_killer2']['variable'], int(args[1])))
                                        OSCorderList.append(OSCOrder('round_killer3', gs.oscJsonProfile['round_killer3']['variable'], int(args[2])))
                                    else:
                                        # In case of 8 pages what value goes into each killer number for OSC changes
                                        result = TerrorID8Pages(args[0], args[1], args[3])
                                        OSCorderList.append(OSCOrder('round_killer1', gs.oscJsonProfile['round_killer1']['variable'], result))
                                        OSCorderList.append(OSCOrder('round_killer2', gs.oscJsonProfile['round_killer2']['variable'], int(args[1])))
                                        OSCorderList.append(OSCOrder('round_killer3', gs.oscJsonProfile['round_killer3']['variable'], int(args[0])))
                                    OSCorderList.append(OSCOrder('round_type', gs.oscJsonProfile['round_type']['variable'], gs.oscJsonProfile['round_type']['values'][args[3]]))
                            case "round_unknown":
                                print('round_unknown placeholder')
                            case "round_possessed":
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values']))
                            case "is_gigabyte":
                                gs.roundType = 'Special'
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values']))
                            case "is_joy_asleep":
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values']))
                            case "is_joy_awake":
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values']))
                            case "is_glorbo":
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values']))
                            case "is_wild_yet_bloodthirsty_creature":
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values']))
                            case "is_atrached":
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values']))
                            case "is_hungry_home_invader":
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values']))
                            case "is_meatball_man":
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values']))
                            case "is_foxy":
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values']))
                            case "round_won":
                                gs.roundCondition = 'WIN'
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values'], 'resetRound'))
                            case "round_lost":
                                gs.roundCondition = 'LOSE'
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values'], 'resetRound'))
                                ResetRound()
                            case "item_pickup":
                                if args[0] in gs.oscJsonProfile[key]['values']:     # First check if the item exists, that list is not refined yet and new items may enter
                                    OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values'][args[0]]))
                                else:
                                    print(f'OSC Alert: item [{args[0]}] is not in the json file')
                            case "item_drop":
                                OSCorderList.append(OSCOrder(key, gs.oscJsonProfile[key]['variable'], gs.oscJsonProfile[key]['values']))

                        
                        OSCorderList = ExecuteOSCList(OSCorderList)         # Process all the OSC calls

                        if key not in ['TONWINTER','TONWAPRIL','TONCODE']:  # Process all Websocket calls
                            SendWSMessage(key, args)

                        break
            
        cursor = i_content.tell()                               # If we are done, recover where the cursor is, which should be at the end
        
        # To prevent saving, if the end of file cursor is None for whatever reason, abort and don't save anything, wait for the next loop
        if cursor is None:
            ErrorLogging(f"Error in ParseContent, cursor is None", True)
            cursor = i_cursor
            codesArray = []
        
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
