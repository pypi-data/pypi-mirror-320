# Graphtomation Documentation

## Installation

Install the required dependencies for Graphtomation using the following command:

```bash
pip install graphtomation
```

---

## Implementation

```py
import requests
from typing import Type
from fastapi import FastAPI
from crewai.tools import BaseTool
from crewai import Agent, Task, Crew
from graphtomation import CrewAIRouter
from pydantic import BaseModel, Field

# Define the input schema for the tool
class DuckDuckGoSearchInput(BaseModel):
    """Input schema for DuckDuckGoSearchTool."""

    query: str = Field(..., description="Search query to look up on DuckDuckGo.")


# Create the custom tool by subclassing BaseTool
class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGoSearch"
    description: str = (
        "This tool performs web searches using DuckDuckGo and retrieves the top results. "
        "Provide a query string to get relevant information."
    )
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

    def _run(self, query: str) -> str:
        """
        Perform a search using the DuckDuckGo API and return the top results.
        """
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_redirect": "1",
            "no_html": "1",
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract the top result or fallback to AbstractText
            if "RelatedTopics" in data and data["RelatedTopics"]:
                results = [
                    topic.get("Text", "No description available")
                    for topic in data["RelatedTopics"]
                    if "Text" in topic
                ]
                return "\n".join(results[:3])  # Return the top 3 results
            else:
                return "No results found for the given query."

        except requests.RequestException as e:
            return f"An error occurred while performing the search: {e}"

ddg_search_tool = DuckDuckGoSearchTool()

researcher = Agent(
    role="Web Researcher",
    goal="Perform searches to gather relevant information for tasks.",
    backstory="An experienced researcher with expertise in online information gathering.",
    tools=[ddg_search_tool],
    verbose=True,
)

research_task = Task(
    description="Search for the latest advancements in AI technology.",
    expected_output="A summary of the top 3 advancements in AI technology from recent searches.",
    agent=researcher,
)

example_crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=True,
    planning=True,
)

app = FastAPI()


crew_router = CrewAIRouter(
    crews=[
        {
            "name": "example-crew",
            "crew": example_crew,
            "metadata": {
                "description": "An example crew ai implementation",
                "version": "1.0.0",
            },
        }
    ]
)

app.include_router(crew_router.router, prefix="/crew")
```

---

## Running the Application

```bash
fastapi dev main.py
```
