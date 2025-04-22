from typing import Dict, NamedTuple, Optional, TYPE_CHECKING, Callable
from BaseClasses import Item, ItemClassification

if TYPE_CHECKING:
    from . import TONWorld

class TONItem(Item):
    game: str = "Terrors of Nowhere"

class TONItemData(NamedTuple):
    code: Optional[int] = None
    classification: ItemClassification = ItemClassification.filler
    can_create: Callable[["TONWorld"], bool] = lambda world: True

dict_of_items_enkp_shop : Dict[str, TONItemData] = {
    "Radar 2" : TONItemData (
        code = 100,
    ),
    "Medkit" : TONItemData (
        code = 101,
        classification = ItemClassification.useful,
    ),
    "HaveBrew" : TONItemData (
        code = 102,
    ),
    "SpeedCoil_Glow" : TONItemData (
        code = 103,
        classification = ItemClassification.useful,
    ),
    "Teleporter" : TONItemData (
        code = 104,
        classification = ItemClassification.useful,
    ),
    "SpeedCoil_1" : TONItemData (
        code = 105,
        classification = ItemClassification.useful,
    ),
    "RegenCoil" : TONItemData (
        code = 106,
        classification = ItemClassification.useful,
    ),
    "MetalBat" : TONItemData (
        code = 107,
        classification = ItemClassification.useful,
    ),
    "KatCharm" : TONItemData (
        code = 108,
        classification = ItemClassification.useful,
    ),
    "CrazyCoil" : TONItemData (
        code = 109,
        classification = ItemClassification.useful,
    ),
    "Glass Coil" : TONItemData (
        code = 110,
    ),
    "CorkScrew" : TONItemData (
        code = 111,
    ),
    "RustyPistol" : TONItemData (
        code = 112,
    ),
    "girlfriend" : TONItemData (
        code = 113,
    ),
}
dict_of_items_surv_shop : [str, TONItemData] = {
    "Burger" : TONItemData (
        code = 201,
    ),
    "BeyondPlush" : TONItemData (
        code = 202,
    ),
    "MagicConchShell" : TONItemData (
        code = 203,
    ),
    "RadarCoil" : TONItemData (
        code = 204,
    ),
    "RubberHammer (Bat)" : TONItemData (
        code = 205,
    ),
    "Banana" : TONItemData (
        code = 206,
    ),
    "TBH" : TONItemData (
        code = 207,
    ),
    "Taser" : TONItemData (
        code = 208,
    ),
    "DarkgreyPlush" : TONItemData (
        code = 209,
    ),
    "Glass Coil X" : TONItemData (
        code = 210,
    ),
    "Emerald Coil" : TONItemData (
        code = 211,
    ),
    "PotOfGreed" : TONItemData (
        code = 212,
    ),
    "Brick" : TONItemData (
        code = 213,
    ),
}
dict_of_items_evnt_shop : [str, TONItemData] = {
    "Luxury Coil" : TONItemData(
        code=301,
    ),
    "Blue Medkit" : TONItemData(
        code=302,
    ),
    "Sealed/Faust/Avenger Sword" : TONItemData(
        code=303,
    ),
    "maxwell" : TONItemData(
        code=304,
    ),
    "Rock" : TONItemData(
        code=305,
    ),
    "Illumina" : TONItemData(
        code=306,
    ),
    "Redbull" : TONItemData(
        code=307,
    ),
    "OmoriPlush" : TONItemData(
        code=308,
    ),
    "ParadiseLost" : TONItemData(
        code=309,
    ),
    "GuidancePlush" : TONItemData(
        code=310,
    ),
    "JOY" : TONItemData(
        code=311,
    ),
    "Jailbird" : TONItemData(
        code=312,
    ),
    "Glognut" : TONItemData(
        code=313,
    ),
    "DevPhone" : TONItemData(
        code=314,
    ),
    "FuwattiPlush" : TONItemData(
        code=315,
    ),
    "SeerPen" : TONItemData(
        code=316,
    ),
    "tamo" : TONItemData(
        code=317,
    ),
    "IJED" : TONItemData(
        code=318,
    ),
    "ItemChest" : TONItemData(
        code=319,
    ),
    "SilverCoil" : TONItemData(
        code=320,
    ),
    "King's Kit" : TONItemData(
        code=321,
    ),
    "Dropkick" : TONItemData(
        code=322,
    ),
}

dict_of_items_filler : Dict[str, TONItemData] = {
    "Nothing" : TONItemData (
        code = 69,
    ),
}

dict_of_completion_items : [str, TONItemData] = {
    "INDEXCOMPLETION" : TONItemData (
        classification = ItemClassification.progression,
        can_create = lambda world: False
    ),
}
'''
dict_of_moon_item : [str, TONItemData] = {
    "Mystic Moon" : TONItemData (
        classification = ItemClassification.progression,
        can_create = lambda world: False
    ),
    "Blood Moon" : TONItemData (
        classification = ItemClassification.progression,
        can_create = lambda world: False
    ),
    "Twilight" : TONItemData (
        classification = ItemClassification.progression,
        can_create = lambda world: False
    ),
    "Solstice" : TONItemData (
        classification = ItemClassification.progression,
        can_create = lambda world: False
    ),
    "All Moons" : TONItemData (
        classification = ItemClassification.progression,
        can_create = lambda world: False
    ),
}
'''

all_items = dict_of_items_enkp_shop | dict_of_items_surv_shop | dict_of_items_evnt_shop | dict_of_items_filler

items_filler = { name : data.code for name, data in dict_of_items_filler.items() if data.code is not None }
items_pool_dict_name2Id = { name : data.code for name, data in all_items.items() if data.code is not None }