from typing import TypedDict, List, Union, Set

class Review(TypedDict):
    review_id: str
    review: str
    voted_up: bool

Dataset = List[Review]

class SteamApp(TypedDict):
    appid: int
    name: str

SteamApps = List[SteamApp]