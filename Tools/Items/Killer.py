import Globals as gs
from Tools.errorHandler import ErrorLogging

class Killer:

    def __init__ (self, i_type, i_id, i_value, i_name):
        self.type = i_type
        self.id = i_id
        self.value = i_value
        self.name = i_name

# Function to translate the raw note data, to something the user can understand
def DecodeNote(i_input):
    try:
        print(f'Reviewing note: {i_input}')

        result = ''
        eventR = ''
        map = ''
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
        else:
            dataRaw = i_input.split(', ')
            map = dataRaw[0]
            round = dataRaw[1]
            
            match round:
                case 'Alternate':
                    roundAux='alternates'

            killersRaw = dataRaw[2].split(' ')
            eventR = dataRaw[3] if len(dataRaw)>3 else ''
            if round.lower() in ['midnight','bloodbath','double trouble','ex','unbound']:    # These rounds have multiple killers
                count = 0
                for killer in killersRaw:
                    match round.lower():
                        case 'midnight':
                            if count == 2:
                                matched = [i for i in gs.killersList if i.type==roundAux and i.id==int(killer)]         # Check for variants
                                if len(matched) == 0:
                                    matched = [i for i in gs.killersList if i.type==roundAux and i.id==int(killer)]     # Check for the alternate
                        case 'unbound':
                            if count == 0:
                                matched = [Killer('unbound', killer, gs.unboundsDict[killer], f'{int(killer)+1}. {gs.unboundsDict[killer]}')]
                            else:               # There's likely only going to be 1 id for unbounds, so exit after getting the first one
                                break

                    # Regular terrors
                    if len(matched) == 0:
                        matched = [i for i in gs.killersList if i.type=='terrors' and i.id==int(killer)]
                    killers.append(matched[0].name)
                    count += 1
                    matched = []
            elif round.lower() in ['mystic moon','blood moon','twilight','solstice','cold night','run']:        # Special rounds
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
            else:                                                                                               # Single killer rounds
                killer = killersRaw[0]
                matched = [i for i in gs.killersList if i.type==roundAux and i.id==int(killer)]            # Check for variants

                if eventR!='' and len(matched)>0:                                                                                  # Special event replacements
                    match eventR:
                        case 'Winterfest':
                            matched[0].name = 'Neo Pilot' if matched[0].value=='fusion_pilot' else matched[0].name

                if len(matched) == 0:                                                                           # Regular terrors
                    matched = [i for i in gs.killersList if i.type=='terrors' and i.id==int(killer)]
                killers.append(matched[0].name)
                matched = []

            for killerName in killers:
                killerStr += killerName + ', '
            killerStr = killerStr[:len(killerStr)-2]            # Remove the last separator from the killers string
            result = f'Won: {map}; {round}; {killerStr}'

        print(f'Note reviewed: {result}')

        return result
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in DecodeNote: {e}")
