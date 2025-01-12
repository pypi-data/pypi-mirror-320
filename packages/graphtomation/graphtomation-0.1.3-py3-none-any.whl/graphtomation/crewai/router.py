from enum import Enum
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Lifespan
from fastapi.routing import BaseRoute, APIRoute
from typing import Callable, Dict, List, Optional, Union, Sequence, Literal, Any, Type

from .executor import CrewExecutor


class CrewApiRouter:
    def __init__(
        self,
        executor: CrewExecutor,
        dependencies: Optional[
            Dict[
                Literal[
                    "list_crews",
                    "train",
                    "kickoff",
                    "kickoff_for_each",
                    "kickoff_for_each_async",
                    "replay",
                    "query_knowledge",
                    "copy",
                    "calculate_usage_metrics",
                    "test",
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
            tags=tags or ["Crew Endpoints"],
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
        Fetch dependencies for a specific route.
        Combines route-specific and global dependencies.
        """
        if route_name in self.dependencies:
            dep_callable = self.dependencies[route_name]
            return [Depends(dep_callable)]
        return []

    def _add_routes(self):
        """
        Add API routes with dynamic dependency resolution.
        """
        self.router.add_api_route(
            "",
            self.executor.list_crews,
            methods=["GET"],
            dependencies=self._get_dependencies("list_crews"),
        )
        self.router.add_api_route(
            "/{name}/train",
            self.executor.train,
            methods=["POST"],
            dependencies=self._get_dependencies("train"),
        )
        self.router.add_api_route(
            "/{name}/kickoff",
            self.executor.kickoff,
            methods=["POST"],
            dependencies=self._get_dependencies("kickoff"),
        )
        self.router.add_api_route(
            "/{name}/kickoff_for_each",
            self.executor.kickoff_for_each,
            methods=["POST"],
            dependencies=self._get_dependencies("kickoff_for_each"),
        )
        self.router.add_api_route(
            "/{name}/kickoff_for_each_async",
            self.executor.kickoff_for_each_async,
            methods=["POST"],
            dependencies=self._get_dependencies("kickoff_for_each_async"),
        )
        self.router.add_api_route(
            "/{name}/replay",
            self.executor.replay,
            methods=["POST"],
            dependencies=self._get_dependencies("replay"),
        )
        self.router.add_api_route(
            "/{name}/query_knowledge",
            self.executor.query_knowledge,
            methods=["POST"],
            dependencies=self._get_dependencies("query_knowledge"),
        )
        self.router.add_api_route(
            "/{name}/copy",
            self.executor.copy,
            methods=["GET"],
            dependencies=self._get_dependencies("copy"),
        )
        self.router.add_api_route(
            "/{name}/calculate_usage_metrics",
            self.executor.calculate_usage_metrics,
            methods=["GET"],
            dependencies=self._get_dependencies("calculate_usage_metrics"),
        )
        self.router.add_api_route(
            "/{name}/test",
            self.executor.test,
            methods=["POST"],
            dependencies=self._get_dependencies("test"),
        )
