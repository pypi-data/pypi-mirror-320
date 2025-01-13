# **Graphtomation Documentation**

**⚠️ Disclaimer: This package is still under development. Use it at your own risk.**

---

## Overview

Graphtomation is an AI utility package designed to simplify the development and deployment of AI-powered workflows. By combining Crew and LangGraph with FastAPI, it enables AI engineers to create modular, reusable components and expose them as API endpoints. With tools, agents, tasks, and crews ready for integration, Graphtomation accelerates the process of building and serving complex multi-agent systems.

---

## Installation

Install the required dependencies for Graphtomation using the following command:

```bash
pip install graphtomation
```

---

## Implementation

### Crew

```py
from typing import Type
from fastapi import FastAPI
from crewai.tools import BaseTool
from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field
from langchain_community.tools import DuckDuckGoSearchRun
from graphtomation.crewai import CrewApiRouter, CrewExecutor


app = FastAPI()


class DuckDuckGoSearchInput(BaseModel):
    """Input schema for DuckDuckGoSearchTool."""

    query: str = Field(..., description="Search query to look up on DuckDuckGo.")


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
        return DuckDuckGoSearchRun().invoke(query)


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


crew_router = CrewApiRouter(
    executor=CrewExecutor(
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
)

app.include_router(crew_router.router, prefix="/crew")
```

### Langgraph

```py
import os
from typing import Literal
from fastapi import FastAPI
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langchain_community.tools import DuckDuckGoSearchRun
from graphtomation.langgraph import GraphExecutor, GraphApiRouter
from langgraph.graph import END, START, StateGraph, MessagesState


app = FastAPI()


@tool(name_or_callable="search-tool")
def search(query: str):
    """Search the web using this tool"""
    return DuckDuckGoSearchRun().invoke(query)


tools = [search]

tool_node = ToolNode(tools)

model = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY")).bind_tools(tools)


def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


def call_model(state: MessagesState):
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}


workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
)

workflow.add_edge("tools", "agent")

graph_router = GraphApiRouter(
    executor=GraphExecutor(
        graphs=[
            {
                "name": "langgraph-chatbot",
                "state_graph": workflow,
                "kwargs": {
                    "checkpointer": {
                        "name": "postgres",
                        "conn_string": os.getenv("DB_CONN_STRING"),
                    },
                },
            }
        ]
    )
)

app.include_router(graph_router.router, prefix="/graphs")
```
