from typing import List, Dict, Optional, TypedDict

from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import AsyncPostgresStore

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.base import BaseCheckpointSaver

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
    StateSnapshotModel,
    GraphArgs,
)


class SingleGraphExecutor:
    def __init__(self, args: GraphArgs):
        self.state_graph = args.get("state_graph")
        self.kwargs = args.get("compile_graph_args")
        self.compiled_graph: Optional[CompiledStateGraph] = None

    @classmethod
    async def from_compiled_graph(cls, args: GraphArgs) -> "SingleGraphExecutor":
        instance = cls(args=args)
        kwargs = instance.kwargs
        store = None
        checkpointer = None

        if kwargs and kwargs.get("store") and kwargs["store"].get("name"):
            store = await cls.initialize_store(config=kwargs["store"])

        if kwargs and kwargs.get("checkpointer") and kwargs["checkpointer"].get("name"):
            checkpointer = await cls.initialize_checkpointer(
                config=kwargs["checkpointer"]
            )

        instance.compiled_graph = await instance.state_graph.compile(
            interrupt_before=kwargs.get("interrupt_before") if kwargs else None,
            interrupt_after=kwargs.get("interrupt_after") if kwargs else None,
            debug=kwargs.get("debug") if kwargs else False,
            checkpointer=checkpointer,
            store=store,
        )
        return instance

    @staticmethod
    async def initialize_store(config: StoreConfig) -> BaseStore:
        index = None
        if (
            config.get("index_dims")
            or config.get("index_embed")
            or config.get("index_fields")
        ):
            index = {
                "dims": config.get("index_dims"),
                "embed": config.get("index_embed"),
                "fields": config.get("index_fields"),
            }

        if config.get("name") == "postgres":
            async with AsyncPostgresStore.from_conn_string(
                conn_string=config.get("conn_string"),
                pool_config=config.get("pool_config"),
                index=index if index else None,
            ) as store:
                await store.setup()
                return store
        elif config.get("name") == "memory":
            return InMemoryStore(index=index if index else None)

        raise ValueError(f"Unsupported store type: {config.get('name')}")

    @staticmethod
    async def initialize_checkpointer(
        config: CheckpointerConfig,
    ) -> BaseCheckpointSaver:
        if config.get("conn_string") and config.get("name") == "postgres":
            conn_string = str(config.get("conn_string"))
            async with AsyncPostgresSaver.from_conn_string(
                conn_string=conn_string
            ) as saver:
                await saver.setup()
                return saver
        elif config.get("name") == "memory":
            return MemorySaver()
        else:
            raise ValueError(f"Unsupported checkpointer type: {config.get('name')}")

    def _ensure_compiled_graph(self):
        if self.compiled_graph is None:
            raise ValueError(
                "Compiled graph is not initialized. Please call `from_compiled_graph`."
            )

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

    async def astream(self, input: GraphStreamInputState):
        self._ensure_compiled_graph()
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


class GraphExecutor:
    def __init__(self, graphs: List[GraphArgs]):
        self.graphs = graphs
        self.graph_executors: Dict[str, SingleGraphExecutor] = {}

    def get_graph(self, name: str) -> SingleGraphExecutor:
        if name not in self.graph_executors:
            graph_args = next(
                (g for g in self.graphs if g.get("kwargs", {}).get("name") == name),
                None,
            )
            if not graph_args:
                raise ValueError(f"Graph '{name}' not found.")
            self.graph_executors[name] = SingleGraphExecutor(graph_args)
        return self.graph_executors[name]

    async def get_executor(self, name: str) -> SingleGraphExecutor:
        if name not in self.graph_executors:
            graph_args = next(
                (g for g in self.graphs if g.get("kwargs", {}).get("name") == name),
                None,
            )
            if not graph_args:
                raise ValueError(f"Graph '{name}' not found.")

            executor = await SingleGraphExecutor.from_compiled_graph(graph_args)
            self.graph_executors[name] = executor

        return self.graph_executors[name]

    async def list_graphs(self):
        result = []
        for graph in self.graphs:
            name = graph.get("kwargs", {}).get("name")
            metadata = graph.get("kwargs", {}).get("metadata")

            graph_executor = await self.get_executor(name)
            schema = await graph_executor.aget_graph_schema(GetGraphSchema(config=None))

            result.append(
                {
                    "name": name,
                    "metadata": metadata,
                    "schema": {
                        "graph_schema": schema.graph_schema,
                        "input_schema": schema.input_schema,
                        "output_schema": schema.output_schema,
                        "config_schema": schema.config_schema,
                    },
                }
            )
        return result

    async def ainvoke(self, name: str, input: GraphInvokeInputState):
        graph_executor = await self.get_executor(name)
        return await graph_executor.ainvoke(input)

    async def abatch(self, name: str, input: GraphBatchInputState):
        graph_executor = await self.get_executor(name)
        return await graph_executor.abatch(input)

    async def abatch_as_completed(
        self, name: str, input: GraphBatchAsCompletedInputState
    ):
        graph_executor = await self.get_executor(name)
        async for result in graph_executor.abatch_as_completed(input):
            yield result

    async def astream(self, name: str, input: GraphStreamInputState):
        graph_executor = await self.get_executor(name)
        async for result in graph_executor.astream(input):
            yield result

    async def aget_state(self, name: str, input: GetGraphState):
        graph_executor = await self.get_executor(name)
        return await graph_executor.aget_state(input)

    async def aget_state_history(self, name: str, input: GetGraphStateHistory):
        graph_executor = await self.get_executor(name)
        async for snapshot in graph_executor.aget_state_history(input):
            yield snapshot

    async def aget_subgraphs(self, name: str, input: GetSubgraphs):
        graph_executor = await self.get_executor(name)
        async for subgraph in graph_executor.aget_subgraphs(input):
            yield subgraph

    async def aget_graph_schema(
        self, name: str, input: GetGraphSchema
    ) -> GetGraphSchemaResponse:
        graph_executor = await self.get_executor(name)
        return await graph_executor.aget_graph_schema(input)

    async def initialize_graph(self, name: str):
        graph_executor = await self.get_executor(name)
        await graph_executor.get_executor(name)
        return {"message": f"Graph '{name}' initialized successfully."}

    async def reload_graph(self, name: str):
        if name in self.graph_executors:
            del self.graph_executors[name]
            self.graph_executors[name] = await self.get_executor(name)
        return {"message": f"Graph '{name}' reloaded successfully."}
