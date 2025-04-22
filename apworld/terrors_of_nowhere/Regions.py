from typing import NamedTuple, List, Dict

class TONRegionData(NamedTuple):
    adjacent : List[str] = []

regions_dict : Dict[str, TONRegionData] = {
    "Menu" : TONRegionData(["Sinners Court"]),
    "Sinners Court" : TONRegionData(),
}