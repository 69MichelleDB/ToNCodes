import Globals as gs
from Tools.errorHandler import ErrorLogging
import re

class Encounters:

    def __init__ (self, i_type, i_id, i_value, i_name, variant_type=None):
        self.type = i_type
        self.id = i_id
        self.value = i_value
        self.name = i_name
        self.variant_type = variant_type

# Function to translate the raw note data, to something the user can understand
def DecodeNote(i_input, nameOnly=False):
    try:
        result = ''
        eventR = ''
        map = ''
        mapRegex = re.compile(r"(^.+?) \((\d+)\)$")     # This is for the map and id
        mapMatched = []
        round = ''
        roundAux = ''
        killers = []
        matched = []
        killerStr = ''
        isMonarch = False

        if i_input == 'No notes':
            print('This is a code from a version without Note integration (< 0.5.0)')
            result = gs.localeDict['Notes-Old-Code']
        elif i_input == 'RESPAWN':
            result = gs.localeDict['Notes-Respawn']
        elif i_input == 'Manual':
            result = gs.localeDict['Notes-Manual']
        else:
            dataRaw = i_input.split(', ')
            map = dataRaw[0]
            mapMatched = mapRegex.search(map).groups()
            round = dataRaw[1]
            
            if round in ['Alternate', 'Fog (Alternate)', 'Ghost (Alternate)','Midnight']:
                roundAux='alternates'
            elif round == 'Unbound':
                roundAux='unbounds'

            killersRaw = dataRaw[2].split(' ')
            eventR = dataRaw[3] if len(dataRaw)>3 else ''

            gs.killersListCurrent = gs.pools

            if len(gs.killersListCurrent)>0:

                roundNameFix = round.lower().replace(' ','')

                if roundNameFix in ['midnight','bloodbath','doubletrouble','ex','unbound']:    # These rounds have multiple killers
                    count = 0
                    for killer in killersRaw:
                        match roundNameFix:
                            case 'midnight':
                                # Check for terror variants in midnight
                                if count < 2:
                                    matched = [i for i in gs.killersListCurrent if i.type==roundNameFix and i.variant_type=='terror' and i.id==int(killer)]
                                else:
                                    # Check for alternate variants in midnight
                                    matched = [i for i in gs.killersListCurrent if i.type==roundNameFix and i.variant_type=='alternate' and i.id==int(killer)]
                                    if len(matched)>0:                                  # We need to check for monarch if a variant was found
                                        if matched[0].id == 19:                         # Check for Monarch, rounds with them in, have no other terrors
                                            isMonarch = True
                                    else:       # If no variant was found, find the alternate
                                        matched = [i for i in gs.killersListCurrent if i.type==roundAux and i.id==int(killer)]
                            case 'unbound':
                                if count == 0:
                                    matched = [i for i in gs.killersListCurrent if i.type==roundAux and i.id==int(killer)]
                                else: 
                                    break   # We only need the first number

                        # Regular terrors
                        if len(matched) == 0:
                            matched = [i for i in gs.killersListCurrent if i.type=='terrors' and i.id==int(killer)]
                        killers.append(matched[0].name)
                        if roundNameFix == 'double trouble' and count == 2:        # In case of double trouble, one of the killers is there twice
                            killers = DoubleTrouble(killers)
                        count += 1
                        matched = []
                elif roundNameFix in ['mysticmoon','bloodmoon','twilight','solstice','coldnight','run', 'special', '8pages']:        # Special rounds
                    match roundNameFix:
                        case 'mysticmoon':
                            killers.append('Psychosis')
                        case 'bloodmoon':
                            killers.append('Virus')
                        case 'twilight':
                            killers.append('Apocalypse Bird')
                        case 'solstice':
                            killers.append('Pandora')
                        case 'coldnight':
                            killers.append('Rift Monsters')
                        case 'run':
                            killers.append('Meatball Man')
                        case 'special':
                            killers.append('GIGABYTES')
                        case '8pages':
                            killer = killersRaw[0]
                            matched = [i for i in gs.killersListCurrent if i.type==roundNameFix and i.id==int(killer)]
                            killers.append(matched[0].name)
                else:                                                                                           # Single killer rounds
                    killer = killersRaw[0]

                    # Check for terror variants in cracked
                    if roundNameFix == 'cracked':
                        matched = [i for i in gs.killersListCurrent if i.type==roundNameFix and i.variant_type=='terror' and i.id==int(killer)]
                    
                    # Special event replacements
                    if eventR!='' and len(matched)>0:
                        match eventR:
                            case 'Winterfest':
                                matched[0].name = 'Neo Pilot' if matched[0].value=='fusion_pilot' else matched[0].name
                    
                    # Check for Alternates
                    matched = [i for i in gs.killersListCurrent if i.type==roundAux and i.id==int(killer)]      

                    # And finally check for regular terrors
                    if len(matched) == 0:                                                                           
                        matched = [i for i in gs.killersListCurrent if i.type=='terrors' and i.id==int(killer)]
                    killers.append(matched[0].name)
                    matched = []
                
                # Name concat
                if isMonarch:
                    killerStr = killers[2]
                else: 
                    for killerName in killers:
                        if eventR == 'AprilFools' and gs.configList['silly-enabled']=='1' and killerName in gs.sillyNames:
                            killerName = killerName.replace(killerName, gs.sillyNames[killerName])
                        killerStr += killerName + ', '
                    killerStr = killerStr[:len(killerStr)-2]            # Remove the last separator from the killers string
                if not nameOnly:
                    result = gs.localeDict['Notes-Structure'].format(round=round, mapMatched=mapMatched[0], killerStr=killerStr)
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