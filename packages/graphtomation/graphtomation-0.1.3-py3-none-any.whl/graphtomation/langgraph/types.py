import os
from uuid import uuid4
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langgraph.graph.state import StateGraph
from langchain.embeddings.base import Embeddings
from pydantic import BaseModel, model_validator
from langgraph.graph.state import RunnableConfig
from langchain_core.runnables.graph import Graph
from langgraph.store.postgres.base import PoolConfig
from langgraph.checkpoint.base import CheckpointMetadata
from typing import Sequence, Any, Union, Optional, Literal, Dict, Type, Tuple


class PregelTaskModel(BaseModel):
    id: str
    name: str
    path: Tuple[Union[str, int, Tuple], ...]
    error: Optional[Any] = Field(
        default=None, description="Error encountered during the task."
    )
    interrupts: Tuple[Any, ...] = Field(
        default=(), description="Interruptions during execution."
    )
    state: Optional[Union[None, "StateSnapshotModel", RunnableConfig]] = Field(
        default=None, description="State information."
    )
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Result of the task."
    )

    class Config:
        arbitrary_types_allowed = True


class StateSnapshotModel(BaseModel):
    values: Union[Dict[str, Any], Any] = Field(
        ..., description="Current values of channels."
    )
    next: Tuple[str, ...] = Field(
        ..., description="Name of the node to execute in each task."
    )
    config: RunnableConfig = Field(
        ..., description="Config used to fetch this snapshot."
    )
    metadata: Optional[CheckpointMetadata] = Field(
        default=None, description="Metadata associated with this snapshot."
    )
    created_at: Optional[str] = Field(
        default=None, description="Timestamp of snapshot creation."
    )
    parent_config: Optional[RunnableConfig] = Field(
        default=None, description="Config used to fetch the parent snapshot."
    )
    tasks: Tuple[PregelTaskModel, ...] = Field(
        ..., description="Tasks to execute in this step."
    )

    class Config:
        arbitrary_types_allowed = True


class GraphInvokeInputState(BaseModel):
    input: Union[Dict[str, Any], Any]
    config: Optional[RunnableConfig] = RunnableConfig(
        configurable={"thread_id": uuid4()}
    )
    stream_mode: Optional[
        Literal["values", "updates", "debug", "messages", "custom"]
    ] = "values"
    output_keys: Optional[Union[str, Sequence[str]]] = None
    interrupt_before: Optional[Union[Literal["*"], Sequence[str]]] = None
    interrupt_after: Optional[Union[Literal["*"], Sequence[str]]] = None
    debug: Optional[bool] = None

    class Config:
        arbitrary_types_allowed = True


class GraphStreamInputState(GraphInvokeInputState):
    subgraphs: bool = False


class GraphBatchInputState(BaseModel):
    inputs: Sequence[Union[Dict[str, Any], Any]]
    config: Optional[Union[RunnableConfig, Sequence[RunnableConfig]]] = None
    return_exceptions: Literal[False] = False

    class Config:
        arbitrary_types_allowed = True


class GraphBatchAsCompletedInputState(GraphBatchInputState):
    pass


class GetGraphState(BaseModel):
    config: RunnableConfig
    subgraphs: bool = False

    class Config:
        arbitrary_types_allowed = True


class GetGraphStateHistory(BaseModel):
    config: RunnableConfig
    filter: Dict[str, Any] | None = None
    before: RunnableConfig | None = None
    limit: int | None = None

    class Config:
        arbitrary_types_allowed = True


class GetSubgraphs(BaseModel):
    namespace: Optional[str] = None
    recurse: bool = False

    class Config:
        arbitrary_types_allowed = True


class GetGraphSchema(BaseModel):
    config: Optional[RunnableConfig] = None
    xray: Optional[Union[int, bool]] = False

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.config is None:
            self.config = RunnableConfig(configurable={})


class GetGraphSchemaResponse(BaseModel):
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]
    config_schema: Type[BaseModel]
    graph_schema: Any

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def validate_components(
        cls, input_schema, output_schema, config_schema, graph_schema
    ):
        if not all(
            isinstance(c, BaseModel)
            for c in [input_schema, output_schema, config_schema]
        ):
            raise TypeError(
                "Input, output, and config schemas must inherit from BaseModel."
            )
        if not isinstance(graph_schema, Graph):
            raise TypeError("Graph schema must be an instance of Graph.")


class CheckpointerConfig(TypedDict):
    name: Optional[Literal["postgres", "memory"]] = None
    conn_string: Optional[str] = os.getenv("DB_CONN_STRING")


class StoreConfig(TypedDict):
    name: Optional[Literal["postgres", "memory"]] = None
    conn_string: Optional[str] = os.getenv("DB_CONN_STRING")
    pool_config: Optional[PoolConfig] = None
    index_dims: Optional[int] = 1536
    index_embed: Optional[Any] = None
    index_fields: Optional[list[str]] = None


class CompileGraphArgs(TypedDict):
    interrupt_before: list[str] | Literal["*"] | None = None
    interrupt_after: list[str] | Literal["*"] | None = None
    debug: Optional[bool] = False
    checkpointer: Optional[CheckpointerConfig] = None
    store: Optional[StoreConfig] = None

    class Config:
        arbitrary_types_allowed = True


class GraphMetadata(TypedDict, total=False):
    tags: Optional[list[str]] = None
    description: Optional[str] = None
    is_published: Optional[bool] = False


class GraphArgs(TypedDict, total=False):
    name: str
    state_graph: StateGraph
    metadata: Optional[GraphMetadata] = None
    compile_graph_args: Optional[CompileGraphArgs] = None


class SerializedCompileGraphArgs(BaseModel):
    interrupt_before: list[str] | Literal["*"] | None = None
    interrupt_after: list[str] | Literal["*"] | None = None
    debug: Optional[bool] = False
    checkpointer: Optional[str] = None
    store: Optional[str] = None


class SerializedGraphResponse(BaseModel):
    name: str
    metadata: Optional[GraphMetadata] = None
    kwargs: Optional[SerializedCompileGraphArgs] = None
