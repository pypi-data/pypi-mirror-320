from typing import List, Dict, Optional, Union, Callable, Any, Sequence, Literal, Type
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    BackgroundTasks,
)
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Lifespan
from fastapi.routing import APIRoute, BaseRoute
from enum import Enum

from .executor import GraphExecutor
from .types import (
    GraphInvokeInputState,
    GraphStreamInputState,
    GraphBatchInputState,
    GraphBatchAsCompletedInputState,
    GetGraphState,
    GetGraphSchema,
    SerializedGraphResponse,
    StateSnapshotModel,
    GetGraphStateHistory,
    GetSubgraphs,
    CheckpointerConfig,
    SerializedCompileGraphArgs,
    StoreConfig,
)


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, channel_id: str, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections[channel_id] = websocket
        except Exception as e:
            print(f"Error accepting WebSocket connection for client {channel_id}: {e}")

    def disconnect(self, channel_id: str):
        self.active_connections.pop(channel_id, None)

    async def send_message(self, channel_id: str, message: dict):
        websocket = self.active_connections.get(channel_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error sending message to client {channel_id}: {e}")


websocket_manager = WebSocketManager()


class GraphApiRouter:
    def __init__(
        self,
        executor: GraphExecutor,
        dependencies: Optional[
            Dict[
                Literal[
                    "invoke",
                    "batch",
                    "stream",
                    "batch_as_completed",
                    "get_state",
                    "get_graph_schema",
                    "get_state_history",
                    "get_subgraphs",
                    "list_graphs",
                    "get_graph",
                ],
                Callable,
            ]
        ] = None,
        global_dependencies: Optional[List[Callable]] = None,
        prefix: str = "",
        tags: Optional[List[Union[str, Enum]]] = None,
        default_response_class: Type[JSONResponse] = JSONResponse,
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        callbacks: Optional[List[BaseRoute]] = None,
        routes: Optional[List[BaseRoute]] = None,
        redirect_slashes: bool = True,
        default: Optional[ASGIApp] = None,
        dependency_overrides_provider: Optional[Any] = None,
        route_class: Type[APIRoute] = APIRoute,
        on_startup: Optional[Sequence[Callable[[], Any]]] = None,
        on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
        lifespan: Optional[Lifespan[Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
    ):
        self.executor = executor
        self.dependencies = dependencies or {}
        self.router = APIRouter(
            prefix=prefix,
            tags=tags or ["Graph API Endpoints"],
            dependencies=global_dependencies or [],
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            dependency_overrides_provider=dependency_overrides_provider,
            route_class=route_class,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=lifespan,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
        )
        self._add_routes()

    def _get_dependencies(self, route_name: str) -> List[Depends]:
        """
        Fetch dependencies dynamically for a given route. Combines route-specific and global dependencies.
        """
        dep_callable = self.dependencies.get(route_name)
        return [Depends(dep_callable)] if dep_callable else []

    def _add_routes(self):
        """
        Define and register all API routes with proper dependency injection.
        """

        @self.router.post(
            "/{graph_name}/invoke", dependencies=self._get_dependencies("invoke")
        )
        async def invoke(graph_name: str, input_data: GraphInvokeInputState):
            executor = await self.executor.get_executor(graph_name)
            return await executor.ainvoke(input_data)

        @self.router.post(
            "/{graph_name}/batch", dependencies=self._get_dependencies("batch")
        )
        async def batch(
            graph_name: str,
            input_data: GraphBatchInputState,
            background_tasks: BackgroundTasks,
        ):
            executor = await self.executor.get_executor(graph_name)

            async def process_batch():
                return await executor.abatch(input_data)

            background_tasks.add_task(process_batch)
            return {"status": "Batch processing started in background"}

        @self.router.get(
            "/{graph_name}/state",
            response_model=StateSnapshotModel,
            dependencies=self._get_dependencies("get_state"),
        )
        async def get_state(graph_name: str, input_data: GetGraphState):
            executor = await self.executor.get_executor(graph_name)
            return await executor.aget_state(input_data)

        @self.router.get(
            "",
            response_model=List[SerializedGraphResponse],
            dependencies=self._get_dependencies("list_graphs"),
        )
        async def list_graphs():
            response = await self.executor.list_graphs()
            print("Final response: {}".format(response))
            return response

        @self.router.post(
            "/{graph_name}/initialize",
            dependencies=self._get_dependencies("initialize_graph"),
        )
        async def initialize_graph(graph_name: str):
            """
            Endpoint to initialize a graph by compiling it.
            """
            try:
                result = await self.executor.initialize_graph(graph_name)
                return {"status": "success", "message": result["message"]}
            except ValueError as e:
                return JSONResponse(
                    content={"status": "error", "message": str(e)}, status_code=404
                )
            except Exception as e:
                return JSONResponse(
                    content={"status": "error", "message": str(e)}, status_code=500
                )

        @self.router.post(
            "/{graph_name}/reload",
            dependencies=self._get_dependencies("reload_graph"),
        )
        async def reload_graph(graph_name: str):
            """
            Endpoint to reload a graph, removing it from the cache and reinitializing.
            """
            try:
                result = await self.executor.reload_graph(graph_name)
                return {"status": "success", "message": result["message"]}
            except ValueError as e:
                return JSONResponse(
                    content={"status": "error", "message": str(e)}, status_code=404
                )
            except Exception as e:
                return JSONResponse(
                    content={"status": "error", "message": str(e)}, status_code=500
                )

        @self.router.websocket("/{graph_name}/stream/{channel_id}")
        async def stream(graph_name: str, websocket: WebSocket, channel_id: str):
            deps = self._get_dependencies("stream")
            for dep in deps:
                await dep(websocket)

            await websocket_manager.connect(channel_id, websocket)
            try:
                executor = await self.executor.get_executor(graph_name)
                async for message in websocket.iter_json():
                    input_data = GraphStreamInputState(**message)
                    async for data in executor.astream(input_data):
                        await websocket_manager.send_message(channel_id, data)
            except WebSocketDisconnect:
                print(f"WebSocket disconnected for client {channel_id}")
            except Exception as e:
                print(f"Error in WebSocket stream for client {channel_id}: {e}")
            finally:
                websocket_manager.disconnect(channel_id)

        @self.router.websocket("/{graph_name}/batch-as-completed/{channel_id}")
        async def batch_as_completed(
            graph_name: str, websocket: WebSocket, channel_id: str
        ):
            deps = self._get_dependencies("batch_as_completed")
            for dep in deps:
                await dep(websocket)

            await websocket_manager.connect(channel_id, websocket)
            try:
                executor = await self.executor.get_executor(graph_name)
                async for message in websocket.iter_json():
                    input_data = GraphBatchAsCompletedInputState(**message)
                    async for result in executor.abatch_as_completed(input_data):
                        await websocket_manager.send_message(channel_id, result)
            except WebSocketDisconnect:
                print(f"WebSocket disconnected for client {channel_id}")
            except Exception as e:
                print(
                    f"Error in WebSocket batch-as-completed for client {channel_id}: {e}"
                )
            finally:
                websocket_manager.disconnect(channel_id)

        @self.router.websocket("/{graph_name}/state-history/{channel_id}")
        async def state_history(graph_name: str, websocket: WebSocket, channel_id: str):
            deps = self._get_dependencies("get_state_history")
            for dep in deps:
                await dep(websocket)

            await websocket_manager.connect(channel_id, websocket)
            try:
                executor = await self.executor.get_executor(graph_name)
                async for message in websocket.iter_json():
                    input_data = GetGraphStateHistory(**message)
                    async for snapshot in executor.aget_state_history(input_data):
                        await websocket_manager.send_message(channel_id, snapshot)
            except WebSocketDisconnect:
                print(f"WebSocket disconnected for client {channel_id}")
            except Exception as e:
                print(f"Error in WebSocket state-history for client {channel_id}: {e}")
            finally:
                websocket_manager.disconnect(channel_id)

        @self.router.websocket("/{graph_name}/subgraphs/{channel_id}")
        async def subgraphs(graph_name: str, websocket: WebSocket, channel_id: str):
            deps = self._get_dependencies("get_subgraphs")
            for dep in deps:
                await dep(websocket)

            await websocket_manager.connect(channel_id, websocket)
            try:
                executor = await self.executor.get_executor(graph_name)
                async for message in websocket.iter_json():
                    input_data = GetSubgraphs(**message)
                    async for subgraph in executor.aget_subgraphs(input_data):
                        await websocket_manager.send_message(channel_id, subgraph)
            except WebSocketDisconnect:
                print(f"WebSocket disconnected for client {channel_id}")
            except Exception as e:
                print(f"Error in WebSocket subgraphs for client {channel_id}: {e}")
            finally:
                websocket_manager.disconnect(channel_id)
