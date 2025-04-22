import typing
from worlds.AutoWorld import WebWorld, World
from BaseClasses import Tutorial, Region
from .Options import TONOptions
from .Items import TONItem, items_pool_dict_name2Id, all_items, dict_of_completion_items
from .Locations import TONLocation, locations_completion_events, GenerateLocations, GenerateLocations2, locations_pool_dict_name2Id, locations_generated
from .Regions import regions_dict

class TONWorldWeb(WebWorld):
    gameTutorial_en = Tutorial(
        "Start here",
        "A tutorial guide to get started",
        "English",
        "setup_en.md",
        "setup/en",
        ["MichelleDB"]
    )
    tutorials = [gameTutorial_en]
    game_info_languages = ['en']

class TONWorld(World):
    """
    Terrors of Nowhere by Beyond is a VRChat game world where you solo or with other players try to survive different creatures for a period of time.
    Survive, unlock achievements, items and fill the index with new information.
    """
    game: str = "Terrors of Nowhere"
    web = TONWorldWeb

    options : TONOptions
    options_dataclass = TONOptions

    item_name_to_id = items_pool_dict_name2Id
    location_name_to_id = locations_pool_dict_name2Id

    topology_present = False


    def create_item(self, name: str) -> TONItem:
        return TONItem(name, all_items[name].classification, all_items[name].code, self.player)

    def create_event(self, event: str) -> TONItem:
        return TONItem(event, dict_of_completion_items[event].classification, None, self.player)

    def create_items(self) -> None:
        item_pool: List[TONItem] = []
        for name, item in all_items.items():
            if item.code and item.can_create(self):
                item_pool.append(self.create_item(name))
        
        # The plan is to have this temporary until I figure anotehr solution
        if len(item_pool)<len(locations_pool_dict_name2Id):
            difference = len(locations_pool_dict_name2Id) - len(item_pool)
            for i in range(0, difference):
                item_pool.append(self.create_item('Nothing'))

        self.multiworld.itempool += item_pool

    def create_regions(self):
        # Create regions.
        for name in regions_dict.keys():
            region = Region(name, self.player, self.multiworld)
            self.multiworld.regions.append(region)

        # Create locations.
        for name, data in regions_dict.items():
            region = self.get_region(name)

            locationUnlocks = {
                "terrors": self.options.nightmare_terrors_index_range,
                "alternates": self.options.nightmare_alternates_index_range,
                "unbounds": self.options.nightmare_unbounds_index_range,
                "locations": self.options.location_index_range,
                "moons": self.options.moon_index_range
            }

            locations_generated2 = GenerateLocations2(locationUnlocks, locations_generated)

            combined_locations = locations_generated2 | locations_completion_events

            region.add_locations({
                loc_name: loc_data.address for loc_name, loc_data in combined_locations.items()
                if loc_data.region == name  and loc_data.can_create(self) 
            }, TONLocation)
            region.add_exits(regions_dict[name].adjacent)

        # Create events
        for loc_name, loc_data in locations_completion_events.items():
            if loc_data.address is None:
                self.get_location(loc_name).place_locked_item(self.create_event(loc_name))
    
    def set_rules(self):
        self.multiworld.completion_condition[self.player] = lambda state: state.has("INDEXCOMPLETION", self.player)

    def fill_slot_data(self) -> typing.Dict[str, typing.Any]:
        return self.options.as_dict("completion_goal", "nightmare_terrors_index_range", 
            "nightmare_alternates_index_range", "nightmare_unbounds_index_range", "location_index_range", "moon_index_range", "death_link")