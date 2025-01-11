from typing import Optional, cast

from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import AsyncPostgresStore

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph, StateGraph

from .types import (
    GraphInvokeInputState,
    GraphStreamInputState,
    GraphBatchInputState,
    GraphBatchAsCompletedInputState,
    GetGraphState,
    GetGraphStateHistory,
    GetSubgraphs,
    GetGraphSchema,
    GetGraphSchemaResponse,
    CheckpointerConfig,
    StoreConfig,
    GraphArgs,
    PregelTaskModel,
    StateSnapshotModel,
)


class GraphExecutor:
    def __init__(self, args: GraphArgs):
        self.state_graph = args.state_graph
        self.kwargs = args.kwargs
        self.compiled_graph: Optional[CompiledStateGraph] = None

    @classmethod
    async def from_compiled_graph(cls, args: GraphArgs) -> "GraphExecutor":
        instance = cls(args=args)
        kwargs = instance.kwargs

        if kwargs and kwargs.store and kwargs.store.name:
            store = await cls.initialize_store(config=kwargs.store)

        if kwargs and kwargs.checkpointer.name is not None:
            checkpointer = await cls.initialize_checkpointer(config=kwargs.checkpointer)

        if kwargs is not None:
            instance.compiled_graph = await instance.state_graph.compile(
                interrupt_before=instance.kwargs.interrupt_before,
                interrupt_after=instance.kwargs.interrupt_after,
                debug=instance.kwargs.debug,
                checkpointer=checkpointer,
                store=store,
            )
        else:
            instance.compiled_graph = await instance.state_graph.compile()

        return instance

    @staticmethod
    async def initialize_store(config: StoreConfig) -> BaseStore:
        index = None
        if config.index_dims or config.index_embed or config.index_fields:
            index = {
                "dims": config.index_dims,
                "embed": config.index_embed,
                "fields": config.index_fields,
            }

        if config.name == "postgres":
            async with AsyncPostgresStore.from_conn_string(
                conn_string=config.conn_string,
                pool_config=config.pool_config,
                index=index if index else None,
            ) as store:
                await store.setup()
                return store
        elif config.name == "memory":
            return InMemoryStore(index=index if index else None)

        raise ValueError(f"Unsupported store type: {config.name}")

    @staticmethod
    async def initialize_checkpointer(
        config: CheckpointerConfig,
    ) -> BaseCheckpointSaver:
        if config.conn_string and config.name == "postgres":
            conn_string = cast(str, config.conn_string)
            async with AsyncPostgresSaver.from_conn_string(
                conn_string=conn_string
            ) as saver:
                await saver.setup()
                return saver
        elif config.name == "memory":
            return MemorySaver()
        else:
            raise ValueError(f"Unsupported checkpointer type: {config.name}")

    def _ensure_compiled_graph(self):
        if self.compiled_graph is None:
            raise ValueError(
                "Compiled graph is not initialized. Please call `from_compiled_graph`."
            )

    # SECTION: Restapi methods
    async def ainvoke(self, input: GraphInvokeInputState):
        self._ensure_compiled_graph()
        return await self.compiled_graph.ainvoke(
            config=input.config,
            debug=input.debug,
            input=input.input,
            stream_mode=input.stream_mode,
            output_keys=input.output_keys,
            interrupt_before=input.interrupt_before,
            interrupt_after=input.interrupt_after,
        )

    async def abatch(self, input: GraphBatchInputState):
        self._ensure_compiled_graph()
        return await self.compiled_graph.abatch(
            inputs=input.inputs,
            config=input.config,
            return_exceptions=input.return_exceptions,
        )

    async def aget_state(self, input: GetGraphState):
        self._ensure_compiled_graph()
        snapshot = await self.compiled_graph.aget_state(
            config=input.config, subgraphs=input.subgraphs
        )
        return StateSnapshotModel(
            config=snapshot.config,
            created_at=snapshot.created_at,
            metadata=snapshot.metadata,
            next=snapshot.next,
            parent_config=snapshot.parent_config,
            tasks=snapshot.tasks,
            values=snapshot.values,
        )

    async def aget_graph_schema(self, input: GetGraphSchema) -> GetGraphSchemaResponse:
        self._ensure_compiled_graph()
        graph = await self.compiled_graph.aget_graph(
            config=input.config, xray=input.xray
        )

        input_schema = self.compiled_graph.get_input_schema(config=input.config)
        output_schema = self.compiled_graph.get_output_schema(config=input.config)
        config_schema = self.compiled_graph.config_schema()

        return GetGraphSchemaResponse(
            graph_schema=graph,
            input_schema=input_schema,
            output_schema=output_schema,
            config_schema=config_schema,
        )

    # SECTION: Realtime websocket methods
    async def astream(self, input: GraphStreamInputState):
        self._ensure_compiled_graph()
        print("Graph Executor astream: ", input)
        async for result in self.compiled_graph.astream(
            input=input.input,
            config=input.config,
            stream_mode=input.stream_mode,
            output_keys=input.output_keys,
            interrupt_before=input.interrupt_before,
            interrupt_after=input.interrupt_after,
            debug=input.debug,
            subgraphs=input.subgraphs,
        ):
            yield result

    async def abatch_as_completed(self, input: GraphBatchAsCompletedInputState):
        self._ensure_compiled_graph()
        async for result in self.compiled_graph.abatch_as_completed(
            inputs=input.inputs,
            config=input.config,
            return_exceptions=input.return_exceptions,
        ):
            yield result

    async def aget_state_history(self, input: GetGraphStateHistory):
        self._ensure_compiled_graph()
        async for snapshot in self.compiled_graph.aget_state_history(
            config=input.config,
            filter=input.filter,
            before=input.before,
            limit=input.limit,
        ):
            yield StateSnapshotModel(
                config=snapshot.config,
                created_at=snapshot.created_at,
                metadata=snapshot.metadata,
                next=snapshot.next,
                parent_config=snapshot.parent_config,
                tasks=snapshot.tasks,
                values=snapshot.values,
            )

    async def aget_subgraphs(self, input: GetSubgraphs):
        self._ensure_compiled_graph()
        async for subgraph in self.compiled_graph.aget_subgraphs(
            namespace=input.namespace, recurse=input.recurse
        ):
            yield subgraph
