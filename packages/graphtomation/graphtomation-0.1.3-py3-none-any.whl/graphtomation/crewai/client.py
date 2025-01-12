import httpx
from typing import Any, Dict, List, Optional, Union


class CrewApiClient:
    """
    A reusable HTTP client class for interacting with the CrewApiRouter API endpoints.
    """

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Union[int, float] = 10.0,
        auth: Optional[httpx.Auth] = None,
    ):
        """
        Initialize the CrewApiClient with a base URL, optional headers, timeout, and authentication.

        Args:
            base_url (str): The base URL for the Crew API.
            headers (Optional[Dict[str, str]]): Default headers to include in requests.
            timeout (Union[int, float]): Timeout for requests in seconds (default is 10.0 seconds).
            auth (Optional[httpx.Auth]): Optional authentication handler (e.g., httpx.BasicAuth).
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.auth = auth

        # Sync client instance
        self._sync_client = httpx.Client(
            base_url=self.base_url, headers=self.headers, timeout=self.timeout, auth=self.auth
        )

        # Async client instance
        self._async_client = httpx.AsyncClient(
            base_url=self.base_url, headers=self.headers, timeout=self.timeout, auth=self.auth
        )

    def close(self):
        """
        Close the synchronous client session.
        """
        self._sync_client.close()

    async def aclose(self):
        """
        Close the asynchronous client session.
        """
        await self._async_client.aclose()

    def list_crews(self) -> List[Dict[str, Any]]:
        """
        Call the `list_crews` endpoint to retrieve a list of crews.

        Returns:
            List[Dict[str, Any]]: Response data from the API.
        """
        response = self._sync_client.get("/")
        response.raise_for_status()
        return response.json()

    async def alist_crews(self) -> List[Dict[str, Any]]:
        """
        Call the `list_crews` endpoint asynchronously to retrieve a list of crews.

        Returns:
            List[Dict[str, Any]]: Response data from the API.
        """
        async with self._async_client as client:
            response = await client.get("/")
            response.raise_for_status()
            return response.json()

    def train(self, name: str, n_iterations: int, filename: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call the `train` endpoint to train a crew.

        Args:
            name (str): The name of the crew.
            n_iterations (int): Number of training iterations.
            filename (str): Filename for training data.
            inputs (Optional[Dict[str, Any]]): Additional input data.

        Returns:
            Dict[str, Any]: Response data from the API.
        """
        payload = {"n_iterations": n_iterations, "filename": filename, "inputs": inputs or {}}
        response = self._sync_client.post(f"/{name}/train", json=payload)
        response.raise_for_status()
        return response.json()

    async def atrain(self, name: str, n_iterations: int, filename: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call the `train` endpoint asynchronously to train a crew.

        Args:
            name (str): The name of the crew.
            n_iterations (int): Number of training iterations.
            filename (str): Filename for training data.
            inputs (Optional[Dict[str, Any]]): Additional input data.

        Returns:
            Dict[str, Any]: Response data from the API.
        """
        payload = {"n_iterations": n_iterations, "filename": filename, "inputs": inputs or {}}
        async with self._async_client as client:
            response = await client.post(f"/{name}/train", json=payload)
            response.raise_for_status()
            return response.json()

    def kickoff(self, name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the `kickoff` endpoint to execute a task for a crew.

        Args:
            name (str): The name of the crew.
            inputs (Dict[str, Any]): Input data for the task.

        Returns:
            Dict[str, Any]: Response data from the API.
        """
        response = self._sync_client.post(f"/{name}/kickoff", json=inputs)
        response.raise_for_status()
        return response.json()

    async def akickoff(self, name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the `kickoff` endpoint asynchronously to execute a task for a crew.

        Args:
            name (str): The name of the crew.
            inputs (Dict[str, Any]): Input data for the task.

        Returns:
            Dict[str, Any]: Response data from the API.
        """
        async with self._async_client as client:
            response = await client.post(f"/{name}/kickoff", json=inputs)
            response.raise_for_status()
            return response.json()

    def kickoff_for_each(self, name: str, inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Call the `kickoff_for_each` endpoint to execute multiple tasks for a crew.

        Args:
            name (str): The name of the crew.
            inputs (List[Dict[str, Any]]): List of input data for each task.

        Returns:
            List[Dict[str, Any]]: Response data from the API.
        """
        response = self._sync_client.post(f"/{name}/kickoff_for_each", json=inputs)
        response.raise_for_status()
        return response.json()

    async def akickoff_for_each(self, name: str, inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Call the `kickoff_for_each` endpoint asynchronously to execute multiple tasks for a crew.

        Args:
            name (str): The name of the crew.
            inputs (List[Dict[str, Any]]): List of input data for each task.

        Returns:
            List[Dict[str, Any]]: Response data from the API.
        """
        async with self._async_client as client:
            response = await client.post(f"/{name}/kickoff_for_each", json=inputs)
            response.raise_for_status()
            return response.json()

    def replay(self, name: str, task_id: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call the `replay` endpoint to replay a task for a crew.

        Args:
            name (str): The name of the crew.
            task_id (str): The ID of the task to replay.
            inputs (Optional[Dict[str, Any]]): Input data for the task.

        Returns:
            Dict[str, Any]: Response data from the API.
        """
        payload = {"inputs": inputs or {}}
        response = self._sync_client.post(f"/{name}/replay", params={"task_id": task_id}, json=payload)
        response.raise_for_status()
        return response.json()

    async def areplay(self, name: str, task_id: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call the `replay` endpoint asynchronously to replay a task for a crew.

        Args:
            name (str): The name of the crew.
            task_id (str): The ID of the task to replay.
            inputs (Optional[Dict[str, Any]]): Input data for the task.

        Returns:
            Dict[str, Any]: Response data from the API.
        """
        payload = {"inputs": inputs or {}}
        async with self._async_client as client:
            response = await client.post(f"/{name}/replay", params={"task_id": task_id}, json=payload)
            response.raise_for_status()
            return response.json()

    def copy(self, name: str) -> Dict[str, Any]:
        """
        Call the `copy` endpoint to copy a crew.

        Args:
            name (str): The name of the crew.

        Returns:
            Dict[str, Any]: Response data from the API.
        """
        response = self._sync_client.get(f"/{name}/copy")
        response.raise_for_status()
        return response.json()

    async def acopy(self, name: str) -> Dict[str, Any]:
        """
        Call the `copy` endpoint asynchronously to copy a crew.

        Args:
            name (str): The name of the crew.

        Returns:
            Dict[str, Any]: Response data from the API.
        """
        async with self._async_client as client:
            response = await client.get(f"/{name}/copy")
            response.raise_for_status()
            return response.json()

    def calculate_usage_metrics(self, name: str) -> Dict[str, Any]:
        """
        Call the `calculate_usage_metrics` endpoint to get crew metrics.

        Args:
            name (str): The name of the crew.

        Returns:
            Dict[str, Any]: Metrics data from the API.
        """
        response = self._sync_client.get(f"/{name}/calculate_usage_metrics")
        response.raise_for_status()
        return response.json()

    async def acalculate_usage_metrics(self, name: str) -> Dict[str, Any]:
        """
        Call the `calculate_usage_metrics` endpoint asynchronously to get crew metrics.

        Args:
            name (str): The name of the crew.

        Returns:
            Dict[str, Any]: Metrics data from the API.
        """
        async with self._async_client as client:
            response = await client.get(f"/{name}/calculate_usage_metrics")
            response.raise_for_status()
            return response.json()

    def test(self, name: str, n_iterations: int, openai_model_name: Optional[str] = None, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call the `test` endpoint to test a crew.

        Args:
            name (str): The name of the crew.
            n_iterations (int): Number of test iterations.
            openai_model_name (Optional[str]): Optional OpenAI model name.
            inputs (Optional[Dict[str, Any]]): Additional input data.

        Returns:
            Dict[str, Any]: Response data from the API.
        """
        payload = {"n_iterations": n_iterations, "openai_model_name": openai_model_name, "inputs": inputs or {}}
        response = self._sync_client.post(f"/{name}/test", json=payload)
        response.raise_for_status()
        return response.json()

    async def atest(self, name: str, n_iterations: int, openai_model_name: Optional[str] = None, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call the `test` endpoint asynchronously to test a crew.

        Args:
            name (str): The name of the crew.
            n_iterations (int): Number of test iterations.
            openai_model_name (Optional[str]): Optional OpenAI model name.
            inputs (Optional[Dict[str, Any]]): Additional input data.

        Returns:
            Dict[str, Any]: Response data from the API.
        """
        payload = {"n_iterations": n_iterations, "openai_model_name": openai_model_name, "inputs": inputs or {}}
        async with self._async_client as client:
            response = await client.post(f"/{name}/test", json=payload)
            response.raise_for_status()
            return response.json()
