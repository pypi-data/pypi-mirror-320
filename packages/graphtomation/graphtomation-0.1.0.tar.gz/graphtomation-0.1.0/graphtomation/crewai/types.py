from crewai import Crew
from typing import Optional
from typing_extensions import TypedDict


class CrewAIArgs(TypedDict, total=False):
    name: str
    crew: Crew
    metadata: Optional[dict] = None
