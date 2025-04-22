from typing import NamedTuple, Optional, Dict, List, TYPE_CHECKING, Callable
from BaseClasses import Location

if TYPE_CHECKING:
    from . import TONWorld

class TONLocation(Location):
    game: str = "Terrors of Nowhere"

class TONLocationData(NamedTuple):
    region : str
    address: Optional[int] = None
    locked_item: Optional[str] = None
    can_create: Callable[["TONWorld"], bool] = lambda world: True

def GenerateLocations(unlocks: Dict[str, int]) -> Dict[str, TONLocationData]:
    result = {}
    #idCounter = 0
    position = 1
    for key, value in unlocks.items():   # Terrors, Alternates, Unbounds, Locations, Moons
        for i in range(0, value):
            result[f'{key}_{i}'] = TONLocationData(
                region = "Sinners Court",
                #address = position*1000 + idCounter,
                address = position*1000 + i,
            )
            #idCounter += 1
        position += 1
    return result

# Rework this one later
def GenerateLocations2(unlocks: Dict[str, int], loc_generated: Dict[str, TONLocationData]) -> Dict[str, TONLocationData]:
    result = {}
    for key, value in unlocks.items():   # Terrors, Alternates, Unbounds, Locations, Moons
        for i in range(0, value):
            result[f'{key}_{i}'] = TONLocationData(
        region = loc_generated[f'{key}_{i}'].region,
        address = loc_generated[f'{key}_{i}'].address
    )
    return result


locations_event: Dict[str, TONLocationData] ={
       "Mystic Moon":TONLocationData(
        region = "Sinners Court",
        locked_item = "Mystic Moon"
    ),
    "Blood Moon":TONLocationData(
        region = "Sinners Court",
        locked_item = "Blood Moon"
    ),
    "Twilight":TONLocationData(
        region = "Sinners Court",
        locked_item = "Twilight"
    ),
    "Solstice":TONLocationData(
        region = "Sinners Court",
        locked_item = "Solstice"
    ),
    "All Moons":TONLocationData(
        region = "Sinners Court",
        locked_item = "Solstice"
    ),
}

locations_completion_events: Dict[str, TONLocationData] ={
       "INDEXCOMPLETION":TONLocationData(
        region = "Sinners Court",
        locked_item = "INDEXCOMPLETION"
    ),
}

locationUnlocks = {
    "terrors": 144,
    "alternates": 36,
    "unbounds": 84,
    "locations": 74,
    "moons": 4
}

locations_generated = GenerateLocations(locationUnlocks)
locations_pool_dict_name2Id = {name : data.address for name, data in locations_generated.items()}