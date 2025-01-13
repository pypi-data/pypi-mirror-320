import httpx
import asyncio
from websockets import connect
from typing import AsyncGenerator, Dict, Optional, Any, List


class GraphApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.http_client = httpx.AsyncClient()

    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()

    # --- REST Endpoints ---

    async def invoke(
        self, graph_name: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke a graph."""
        url = f"{self.base_url}/{graph_name}/invoke"
        response = await self.http_client.post(url, json=input_data)
        response.raise_for_status()
        return response.json()

    async def batch(
        self, graph_name: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit a batch to the graph."""
        url = f"{self.base_url}/{graph_name}/batch"
        response = await self.http_client.post(url, json=input_data)
        response.raise_for_status()
        return response.json()

    async def get_state(
        self, graph_name: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retrieve the current state of a graph."""
        url = f"{self.base_url}/{graph_name}/state"
        response = await self.http_client.get(url, params=input_data)
        response.raise_for_status()
        return response.json()

    async def initialize_graph(self, graph_name: str) -> Dict[str, Any]:
        """Initialize a graph."""
        url = f"{self.base_url}/{graph_name}/initialize"
        response = await self.http_client.post(url)
        response.raise_for_status()
        return response.json()

    async def reload_graph(self, graph_name: str) -> Dict[str, Any]:
        """Reload a graph."""
        url = f"{self.base_url}/{graph_name}/reload"
        response = await self.http_client.post(url)
        response.raise_for_status()
        return response.json()

    async def list_graphs(self) -> List[Dict[str, Any]]:
        """List all graphs."""
        url = f"{self.base_url}/"
        response = await self.http_client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_graph(self, graph_name: str) -> Dict[str, Any]:
        """Get details about a specific graph."""
        url = f"{self.base_url}/{graph_name}"
        response = await self.http_client.get(url)
        response.raise_for_status()
        return response.json()

    # --- WebSocket Endpoints ---

    async def stream(
        self,
        graph_name: str,
        channel_id: str,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream data from a graph."""
        url = f"{self.base_url.replace('http', 'ws')}/{graph_name}/stream/{channel_id}"
        async with connect(url) as websocket:
            if input_data:
                await websocket.send_json(input_data)
            try:
                while True:
                    message = await websocket.recv()
                    yield message
            except Exception as e:
                print(f"Error during WebSocket streaming: {e}")

    async def batch_as_completed(
        self,
        graph_name: str,
        channel_id: str,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream batch results as they complete."""
        url = f"{self.base_url.replace('http', 'ws')}/{graph_name}/batch-as-completed/{channel_id}"
        async with connect(url) as websocket:
            if input_data:
                await websocket.send_json(input_data)
            try:
                while True:
                    message = await websocket.recv()
                    yield message
            except Exception as e:
                print(f"Error during WebSocket batch-as-completed: {e}")

    async def state_history(
        self,
        graph_name: str,
        channel_id: str,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream the state history of a graph."""
        url = f"{self.base_url.replace('http', 'ws')}/{graph_name}/state-history/{channel_id}"
        async with connect(url) as websocket:
            if input_data:
                await websocket.send_json(input_data)
            try:
                while True:
                    message = await websocket.recv()
                    yield message
            except Exception as e:
                print(f"Error during WebSocket state-history: {e}")

    async def subgraphs(
        self,
        graph_name: str,
        channel_id: str,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream the subgraphs of a graph."""
        url = (
            f"{self.base_url.replace('http', 'ws')}/{graph_name}/subgraphs/{channel_id}"
        )
        async with connect(url) as websocket:
            if input_data:
                await websocket.send_json(input_data)
            try:
                while True:
                    message = await websocket.recv()
                    yield message
            except Exception as e:
                print(f"Error during WebSocket subgraphs: {e}")
