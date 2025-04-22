from dataclasses import dataclass
from Options import Choice, Range, DeathLink, PerGameCommonOptions, StartInventoryPool

class CompletionGoal(Choice):
    """
    Index Completion: You need to see a number of index entries to win (from Nightmare, Location or Moon index)
    Nightmare Index: You need to unlock a randomly selected number of index entries to win (Nightmare index only)
    Locations Index: You need to unlock a randomly selected number of index entries to win (Locations index only)
    Moon Index: You need to unlock a randomly selected number of index entries to win (Moon index only)
    """
    display_name = "Completion goal"
    option_index_completion = 0

class NightmareTerrorsIndexRange(Range):
    """Ramdom Number of entries to unlock from the Nightmare index (Terrors)"""
    display_name = "Nightmare index range (Terrors)"
    range_start = 0
    range_end = 144
    default = 70

class NightmareAlternatesIndexRange(Range):
    """Ramdom Number of entries to unlock from the Nightmare index (Alternates)"""
    display_name = "Nightmare index range (Alternates)"
    range_start = 0
    range_end = 36
    default = 3

class NightmareUnboundsIndexRange(Range):
    """Ramdom Number of entries to unlock from the Nightmare index (Unbounds)"""
    display_name = "Nightmare index range (Unbounds)"
    range_start = 0
    range_end = 84
    default = 1

class LocationIndexRange(Range):
    """Ramdom Number of entries to unlock from the Location index"""
    display_name = "Location index range"
    range_start = 0
    range_end = 74
    default = 30

class MoonsIndexRange(Range):
    """Ramdom Number of entries to unlock from the Moons index"""
    display_name = "Moon index range"
    range_start = 0
    range_end = 4
    default = 1


@dataclass
class TONOptions(PerGameCommonOptions):
    completion_goal: CompletionGoal
    nightmare_terrors_index_range: NightmareTerrorsIndexRange
    nightmare_alternates_index_range: NightmareAlternatesIndexRange
    nightmare_unbounds_index_range: NightmareUnboundsIndexRange
    location_index_range: LocationIndexRange
    moon_index_range: MoonsIndexRange
    death_link: DeathLink
    start_inventory_from_pool: StartInventoryPool