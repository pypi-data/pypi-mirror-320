from enum import Enum
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Lifespan
from fastapi.routing import BaseRoute, APIRoute
from typing import Callable, Dict, List, Optional, Union, Sequence, Literal, Any, Type

from .service import CrewAIService


class CrewAIRouter:
    def __init__(
        self,
        service: CrewAIService,
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
        self.service = service
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

    def _add_routes(self):
        """
        Add API routes with support for route-specific dependencies.
        """
        self.router.add_api_route(
            "",
            self.service.list_crews,
            methods=["GET"],
            dependencies=[Depends(self.dependencies.get("list_crews"))] if "list_crews" in self.dependencies else None,
        )
        self.router.add_api_route(
            "/{name}/train",
            self.service.train,
            methods=["POST"],
            dependencies=[Depends(self.dependencies.get("train"))] if "train" in self.dependencies else None,
        )
        self.router.add_api_route(
            "/{name}/kickoff",
            self.service.kickoff,
            methods=["POST"],
            dependencies=[Depends(self.dependencies.get("kickoff"))] if "kickoff" in self.dependencies else None,
        )
        self.router.add_api_route(
            "/{name}/kickoff_for_each",
            self.service.kickoff_for_each,
            methods=["POST"],
            dependencies=[Depends(self.dependencies.get("kickoff_for_each"))] if "kickoff_for_each" in self.dependencies else None,
        )
        self.router.add_api_route(
            "/{name}/kickoff_for_each_async",
            self.service.kickoff_for_each_async,
            methods=["POST"],
            dependencies=[Depends(self.dependencies.get("kickoff_for_each_async"))] if "kickoff_for_each_async" in self.dependencies else None,
        )
        self.router.add_api_route(
            "/{name}/replay",
            self.service.replay,
            methods=["POST"],
            dependencies=[Depends(self.dependencies.get("replay"))] if "replay" in self.dependencies else None,
        )
        self.router.add_api_route(
            "/{name}/query_knowledge",
            self.service.query_knowledge,
            methods=["POST"],
            dependencies=[Depends(self.dependencies.get("query_knowledge"))] if "query_knowledge" in self.dependencies else None,
        )
        self.router.add_api_route(
            "/{name}/copy",
            self.service.copy,
            methods=["GET"],
            dependencies=[Depends(self.dependencies.get("copy"))] if "copy" in self.dependencies else None,
        )
        self.router.add_api_route(
            "/{name}/calculate_usage_metrics",
            self.service.calculate_usage_metrics,
            methods=["GET"],
            dependencies=[Depends(self.dependencies.get("calculate_usage_metrics"))] if "calculate_usage_metrics" in self.dependencies else None,
        )
        self.router.add_api_route(
            "/{name}/test",
            self.service.test,
            methods=["POST"],
            dependencies=[Depends(self.dependencies.get("test"))] if "test" in self.dependencies else None,
        )
