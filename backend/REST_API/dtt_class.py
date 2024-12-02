from pydantic import BaseModel
from typing import List

class MainPage(BaseModel):
    genre: str
    netflix_selected: bool
    tving_selected: bool
    coupang_selected: bool
    watcha_selected: bool
    wavve_selected: bool

class SearchPage(BaseModel):
    searchString: str
    netflix_selected: bool
    tving_selected: bool
    coupang_selected: bool
    watcha_selected: bool
    wavve_selected: bool

class ReturnMovie(BaseModel):
    title: str
    genre: List[str]
    age_rating: str
    country: List[str]
    year: str
    running_time: int
    description: str
    poster_url: str
    actor: List[str]
    staff: List[str]
    ott_provider: List[str]