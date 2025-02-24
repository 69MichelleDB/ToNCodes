import Globals as gs
from Tools.errorHandler import ErrorLogging

# Check the content of a log and parse all data
def ParseContent(i_content, i_fileName, i_cursor):
    try: 
        # 2025.02.16 23:58:03 Log        -  This round is taking place at Inner Tower (24) and the round type is Classic
        # 2025.02.16 23:58:13 Log        -  Killers have been set - 120 0 0 // Round type is Classic
        
        # 2025.02.16 23:59:04 Log        -  You died.
        # 2025.02.16 23:59:05 Log        -  Died in round.
        # 2025.02.17 00:02:32 Log        -  WE WON
        # 2025.02.17 00:02:32 Log        -  Lived in round.

    # 2025.02.17 14:48:04 Log        -  Respawned? Coward.
    # 2025.02.17 14:48:04 Log        -  Player respawned, opted out!
        
        # 2025.02.17 14:48:05 Log        -  saved
        # 2025.02.17 00:02:38 Log        -  [START]096665_9_3_3896_838...[END]

        cursor = i_cursor

        codesArray = []

        strCodeStart = "Debug      -  [START]"
        strKillerSet = "Killers have been set - "
        strMapSet = "This round is taking place at "
        strDed = "You died."
        strWin = "Lived in round."
        strRespawn = "Respawned? Coward."

        # First check if there's anything in the log
        cursorRespawn = i_content.find(strRespawn, cursor)
        cursorWin = i_content.find(strWin, cursor)
        cursorDead = i_content.find(strDed, cursor)
        cursorMap = i_content.find(strMapSet, cursor)
        cursorKiller = i_content.find(strKillerSet, cursor)
        cursorCode = i_content.find(strCodeStart, cursor)
        
        # If there's nothing after the cursor, move on
        if cursorRespawn == -1 and cursorWin == -1 and cursorDead == -1 and cursorMap == -1 and cursorKiller == -1 and cursorCode == -1:
            cursor = len(i_content)

        # So, there's something, let's read the file
        while cursor < len(i_content):
            # The player can respawn at any point, I need to know if the next respawn is before or after the next condition to find
            cursorRespawn = i_content.find(strRespawn, cursor)            # Rewpawning can happen at any point
#region MAP
            if gs.roundMap == '':           # If map wasn't defined, search for it...                   ## FINDING MAP
                print("Map's not defined, searching...")
                cursor = i_content.find(strMapSet, cursor)
                if cursor != -1 and cursorRespawn !=-1:             # Map and Respawn
                    if cursor < cursorRespawn:                      # Is map or respawn first?
                        endIndex = i_content.find("\n", cursor)
                        newMapRaw = i_content[cursor + len(strMapSet):endIndex]
                        gs.roundMap = newMapRaw.replace(' and the round type is ',', ')
                        print(f"New map found: [{gs.roundMap}] round started.")
                    else: 
                        print("User respawned!!!")
                        gs.roundCondition = 'RESPAWN'
                        cursor = cursorRespawn
                elif cursor != -1 and cursorRespawn == -1:          # Only map
                    endIndex = i_content.find("\n", cursor)
                    newMapRaw = i_content[cursor + len(strMapSet):endIndex]
                    gs.roundMap = newMapRaw.replace(' and the round type is ',', ')
                    print(f"New map found: [{gs.roundMap}] round started.")
                elif cursor == -1 and cursorRespawn != -1:          # Only respawn
                    print("User respawned!!!")
                    gs.roundCondition = 'RESPAWN'
                    cursor = cursorRespawn
                else:                                               # Neither
                    print("No map, no respawn, move along.")
                    cursor = len(i_content)               # Place the cursor at the end of the file
# region KILLER
            elif gs.roundKiller == '':                                                                  ## MAP FOUND
                print(f"Searching for killer...")                      ## FINDING KILLER
                cursor = i_content.find(strKillerSet, cursor)
                if cursor == -1:                        # If no killer's found, out
                    cursor = len(i_content)             # Place the cursor at the end of the file
                else:                                   # Map found...
                    endIndex = i_content.find(" // Round type is", cursor)
                    newKillerRaw = i_content[cursor + len(strKillerSet):endIndex]
                    gs.roundKiller = newKillerRaw
                    print(f"New killer found: [{gs.roundKiller}].")
                    cursor = i_content.find("\n", endIndex)
# region CONDITION
            elif gs.roundCondition == '':
                # We need to check what's the closest condition
                cursorWin = i_content.find(strWin, cursor)
                cursorDead = i_content.find(strDed, cursor)
                
                if cursorWin != -1 and cursorDead != -1 and cursorRespawn != -1:            # W D R
                    if cursorWin<cursorDead and cursorWin<cursorRespawn:
                        print("Player won the round.")
                        gs.roundCondition = 'WIN'
                        cursor = cursorWin
                    elif cursorDead<cursorWin and cursorDead<cursorRespawn:
                        print("Player died during the round. Restarting variables...")
                        gs.roundCondition = 'LOSE'
                        cursor = cursorDead
                        gs.roundMap = ''
                        gs.roundKiller = ''
                        gs.roundCondition = ''
                    elif cursorRespawn<cursorWin and cursorRespawn<cursorDead:
                        print("User respawned!!!")
                        gs.roundCondition = 'RESPAWN'
                        cursor = cursorRespawn
                elif cursorWin != -1 and cursorDead != -1 and cursorRespawn == -1:          # W D
                    if cursorWin<cursorDead:
                        print("Player won the round.")
                        gs.roundCondition = 'WIN'
                        cursor = cursorWin
                    else:
                        print("Player died during the round. Restarting variables...")
                        gs.roundCondition = 'LOSE'
                        cursor = cursorDead
                        gs.roundMap = ''
                        gs.roundKiller = ''
                        gs.roundCondition = ''
                elif cursorWin != -1 and cursorDead == -1 and cursorRespawn != -1:          # W R
                    if cursorWin<cursorRespawn:
                        print("Player won the round.")
                        gs.roundCondition = 'WIN'
                        cursor = cursorWin
                    else:
                        print("User respawned!!!")
                        gs.roundCondition = 'RESPAWN'
                        cursor = cursorRespawn
                elif cursorWin == -1 and cursorDead != -1 and cursorRespawn != -1:          # D R
                    if cursorDead<cursorRespawn:
                        print("Player died during the round. Restarting variables...")
                        gs.roundCondition = 'LOSE'
                        cursor = cursorDead
                        gs.roundMap = ''
                        gs.roundKiller = ''
                        gs.roundCondition = ''
                    else:
                        print("User respawned!!!")
                        gs.roundCondition = 'RESPAWN'
                        cursor = cursorRespawn
                elif cursorWin != -1 and cursorDead == -1 and cursorRespawn == -1:          # W
                    print("Player won the round.")
                    gs.roundCondition = 'WIN'
                    cursor = cursorWin
                elif cursorWin == -1 and cursorDead != -1 and cursorRespawn == -1:          # D
                    print("Player died during the round. Restarting variables...")
                    gs.roundCondition = 'LOSE'
                    cursor = cursorDead
                    gs.roundMap = ''
                    gs.roundKiller = ''
                    gs.roundCondition = ''
                elif cursorWin == -1 and cursorDead == -1 and cursorRespawn != -1:          # R
                    print("User respawned!!!")
                    gs.roundCondition = 'RESPAWN'
                    cursor = cursorRespawn
                else:                                                                       # Nothing, leave
                    cursor = len(i_content)
#region Code
            if gs.roundCondition in ['WIN','RESPAWN']:                          # As far as I know only winning and respawning generate a code
                print(f'Code condition fulfilled: {gs.roundCondition}, finding new code.')
                cursor = i_content.find(strCodeStart, cursor)
                if cursor == -1:                            # If there's no codes yet, get out
                    cursor = len(i_content)                 # Place the cursor at the end of the file
                else:
                    # If we find codes, otherwise start parsing the data to split code and datetime
                    print('Code found...')
                    endIndex = i_content.find("[END]", cursor)
                    codeFound = i_content[cursor + len(strCodeStart):endIndex]
                    logLineStart = i_content.rfind('\n', 0, cursor) + 1
                    dateTime = i_content[logLineStart:cursor].strip().split(" Log")[0]
                    note = gs.roundCondition if gs.roundCondition == 'RESPAWN' else f"{gs.roundMap}, {gs.roundKiller}"
                    codesArray.append((i_fileName, dateTime, codeFound, note))
                    cursor = endIndex + len("[END]")

                    print("Code stored. Restarting variables...")
                    gs.roundMap = ''
                    gs.roundKiller = ''
                    gs.roundCondition = ''

        return cursor, codesArray
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ParseContent: {e}")