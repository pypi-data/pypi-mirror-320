from typing import List, Dict, Any, Optional
from .types import CrewArgs
from crewai import Task, Agent


class CrewExecutor:
    def __init__(self, crews: List[CrewArgs]):
        self.crews = crews

    def get_crew(self, name: str) -> CrewArgs:
        crew = next((c for c in self.crews if c["name"] == name), None)
        if not crew:
            raise ValueError(f"Crew '{name}' not found.")
        return crew

    async def list_crews(self):
        def serialize_agent(agent: Agent):
            return {
                "id": str(agent.id),
                "role": agent.role,
                "goal": agent.goal,
                "backstory": agent.backstory,
                "cache": agent.cache,
                "verbose": agent.verbose,
                "max_rpm": agent.max_rpm,
                "allow_delegation": agent.allow_delegation,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "result_as_answer": tool.result_as_answer,
                        "args_schema": tool.args_schema.model_json_schema(),
                    }
                    for tool in agent.tools or []
                ],
                "formatting_errors": agent.formatting_errors,
                "max_iter": agent.max_iter,
                "max_tokens": agent.max_tokens,
                "config": agent.config,
                "crew": str(agent.crew.id) if agent.crew else None,
            }

        def serialize_task(task: Task):
            return {
                "id": str(task.id),
                "name": task.name,
                "description": task.description,
                "expected_output": task.expected_output,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "result_as_answer": tool.result_as_answer,
                        "args_schema": tool.args_schema.model_json_schema(),
                    }
                    for tool in task.tools or []
                ],
                "agent": serialize_agent(task.agent) if task.agent else None,
                "async_execution": task.async_execution,
                "output_file": task.output_file,
                "human_input": task.human_input,
                "start_time": task.start_time.isoformat() if task.start_time else None,
                "end_time": task.end_time.isoformat() if task.end_time else None,
                "execution_duration": task.execution_duration,
                "used_tools": task.used_tools,
                "tools_errors": task.tools_errors,
                "delegations": task.delegations,
                "processed_by_agents": list(task.processed_by_agents),
                "config": task.config,
                "callback": str(task.callback) if task.callback else None,
                "context": [
                    serialize_task(context_task) for context_task in task.context or []
                ],
                "output_json": (
                    task.output_json.model_json_schema() if task.output_json else None
                ),
                "output_pydantic": (
                    task.output_pydantic.model_json_schema()
                    if task.output_pydantic
                    else None
                ),
                "retry_count": task.retry_count,
                "max_retries": task.max_retries,
                "guardrail": str(task.guardrail) if task.guardrail else None,
                "converter_cls": (
                    task.converter_cls.__name__ if task.converter_cls else None
                ),
            }

        serialized_crews = [
            {
                "name": crew["name"],
                "metadata": crew.get("metadata"),
                "crew": {
                    "id": str(crew["crew"].id),
                    "tasks": [serialize_task(task) for task in crew["crew"].tasks],
                    "agents": [serialize_agent(agent) for agent in crew["crew"].agents],
                },
            }
            for crew in self.crews
        ]
        return serialized_crews

    async def train(
        self,
        name: str,
        n_iterations: int,
        filename: str,
        inputs: Optional[Dict[str, Any]] = {},
    ):
        crew = self.get_crew(name)
        crew["crew"].train(n_iterations, filename, inputs)
        return {"message": f"Training for crew '{name}' completed successfully."}

    async def kickoff(self, name: str, inputs: Dict[str, Any]):
        crew = self.get_crew(name)
        result = crew["crew"].kickoff(inputs)
        return result

    async def kickoff_for_each(self, name: str, inputs: List[Dict[str, Any]]):
        crew = self.get_crew(name)
        results = crew["crew"].kickoff_for_each(inputs)
        return results

    async def kickoff_for_each_async(self, name: str, inputs: List[Dict[str, Any]]):
        crew = self.get_crew(name)
        results = await crew["crew"].kickoff_for_each_async(inputs)
        return results

    async def replay(
        self, name: str, task_id: str, inputs: Optional[Dict[str, Any]] = {}
    ):
        crew = self.get_crew(name)
        result = crew["crew"].replay(task_id, inputs)
        return result

    async def query_knowledge(self, name: str, query: List[str]):
        crew = self.get_crew(name)
        results = crew["crew"].query_knowledge(query)
        return results

    async def copy(self, name: str):
        crew = self.get_crew(name)
        copied_crew = crew["crew"].copy()
        return {
            "message": f"Crew '{name}' copied successfully.",
            "crew_id": str(copied_crew.id),
        }

    async def calculate_usage_metrics(self, name: str):
        crew = self.get_crew(name)
        metrics = crew["crew"].calculate_usage_metrics()
        return metrics

    async def test(
        self,
        name: str,
        n_iterations: int,
        openai_model_name: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
    ):
        crew = self.get_crew(name)
        crew["crew"].test(n_iterations, openai_model_name, inputs)
        return {"message": f"Testing for crew '{name}' completed successfully."}
