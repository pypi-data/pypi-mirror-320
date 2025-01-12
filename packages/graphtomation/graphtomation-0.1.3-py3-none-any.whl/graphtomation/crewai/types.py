from crewai import Crew
from typing import Optional
from typing_extensions import TypedDict


class CrewArgs(TypedDict, total=False):
    name: str
    crew: Crew
    metadata: Optional[dict] = None
