import Globals as gs
from Tools.errorHandler import ErrorLogging
import re

class Killer:

    def __init__ (self, i_type, i_id, i_value, i_name):
        self.type = i_type
        self.id = i_id
        self.value = i_value
        self.name = i_name

# Function to translate the raw note data, to something the user can understand
def DecodeNote(i_input, nameOnly=False):
    try:
        result = ''
        eventR = ''
        map = ''
        mapRegex = re.compile(r"(^.+?) \((\d+)\)$")
        mapMatched = []
        round = ''
        roundAux = ''
        killers = []
        matched = []
        killerStr = ''

        if i_input == 'No notes':
            print('This is a code from a version without Note integration (< 0.5.0)')
            result = '[No note, code prior to alpha-0.5.0]'
        elif i_input == 'RESPAWN':
            result = 'Respawned'
        elif i_input == 'Manual':
            result = 'Manual code'
        else:
            dataRaw = i_input.split(', ')
            map = dataRaw[0]
            mapMatched = mapRegex.search(map).groups()
            round = dataRaw[1]
            
            if round in ['Alternate', 'Fog (Alternate)', 'Ghost (Alternate)','Midnight']:
                roundAux='alternates'

            killersRaw = dataRaw[2].split(' ')
            eventR = dataRaw[3] if len(dataRaw)>3 else ''

            match eventR:
                case '':
                    gs.killersListCurrent = gs.killersList
                case 'AprilFools':
                    gs.killersListCurrent = gs.killersListSilly

            if round.lower() in ['midnight','bloodbath','double trouble','ex','unbound']:    # These rounds have multiple killers
                count = 0
                for killer in killersRaw:
                    match round.lower():
                        case 'midnight':
                            if count == 2:
                                matched = [i for i in gs.killersListCurrent if i.type==roundAux and i.id==int(killer)]         # Check for variants
                                if len(matched) == 0:
                                    matched = [i for i in gs.killersListCurrent if i.type==roundAux and i.id==int(killer)]     # Check for the alternate
                        case 'unbound':
                            if count == 0:
                                matched = [Killer('unbound', killer, gs.unboundsDict[killer], f'{int(killer)+1}. {gs.unboundsDict[killer]}')]
                            else:               # There's likely only going to be 1 id for unbounds, so exit after getting the first one
                                break

                    # Regular terrors
                    if len(matched) == 0:
                        matched = [i for i in gs.killersListCurrent if i.type=='terrors' and i.id==int(killer)]
                    killers.append(matched[0].name)
                    if round.lower() == 'double trouble' and count == 2:        # In case of double trouble, one of the killers is there twice
                        killers = DoubleTrouble(killers)
                    count += 1
                    matched = []
            elif round.lower() in ['mystic moon','blood moon','twilight','solstice','cold night','run', 'special', '8pages']:        # Special rounds
                match round.lower():
                    case 'mystic moon':
                        killers.append('Psychosis')
                    case 'blood moon':
                        killers.append('Virus')
                    case 'twilight':
                        killers.append('Apocalypse Bird')
                    case 'solstice':
                        killers.append('Pandora')
                    case 'cold night':
                        killers.append('Rift Monsters')
                    case 'run':
                        killers.append('Meatball Man')
                    case 'special':
                        killers.append('GIGABYTES')
                    case '8pages':
                        killer = killersRaw[0]
                        matched = [i for i in gs.killersListCurrent if i.type==round and i.id==int(killer)]
                        killers.append(matched[0].name)
            else:                                                                                          # Single killer rounds
                killer = killersRaw[0]
                matched = [i for i in gs.killersListCurrent if i.type==roundAux and i.id==int(killer)]            # Check for variants

                if eventR!='' and len(matched)>0:                                                                                  # Special event replacements
                    match eventR:
                        case 'Winterfest':
                            matched[0].name = 'Neo Pilot' if matched[0].value=='fusion_pilot' else matched[0].name

                if len(matched) == 0:                                                                           # Regular terrors
                    matched = [i for i in gs.killersListCurrent if i.type=='terrors' and i.id==int(killer)]
                killers.append(matched[0].name)
                matched = []

            for killerName in killers:
                killerStr += killerName + ', '
            killerStr = killerStr[:len(killerStr)-2]            # Remove the last separator from the killers string
            if not nameOnly:
                result = f'{round} in {mapMatched[0]}: {killerStr}'
                print(f'Note reviewed: {result}')
            else:
                result = killerStr

        return result
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in DecodeNote: {e}")

# In case of double trouble, a Bloodbath round tries to happen but one of the killers spawn twice but stronger.
# I'm not sure if the repeated killer's place in the log changes or it's always the same, I'll assume it changes to prevent issues later and make this function.
def DoubleTrouble (i_killers):
    result = []

    k1 = ''
    k1Count = 0
    k2 = ''
    k2Count = 0
    for killerDT in i_killers:                              # We just look for which killer is there twice
        if k1 == '':
            k1 = killerDT
            k1Count = 1
        elif k2 == '':
            k2 = killerDT
            k2Count = 1
        elif k1 == killerDT:
            k1Count += 1
        elif k2 == killerDT:
            k2Count += 1

    result.append(k1 if k1Count == 1 else f'{k1} Lv.2')     # Send a new list with the killers properly parsed
    result.append(k2 if k2Count == 1 else f'{k2} Lv.2')

    return result