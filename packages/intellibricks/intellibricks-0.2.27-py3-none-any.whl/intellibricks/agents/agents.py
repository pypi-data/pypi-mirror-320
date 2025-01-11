from __future__ import annotations

from itertools import chain
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    Literal,
    Optional,
    Sequence,
    TypedDict,
    cast,
)

from architecture.extensions import Maybe
import msgspec
from architecture.utils import run_sync
from architecture.utils.decorators import ensure_module_installed

from intellibricks.llms import Synapse
from intellibricks.llms.schema import (
    ChatCompletion,
    DeveloperMessage,
    GenerationConfig,
    Message,
    MessageFactory,
    MessageSequence,
    MessageType,
    RawResponse,
    ToolCall,
    ToolCallSequence,
    TraceParams,
    UserMessage,
)
from intellibricks.llms.synapses import SynapticFallbackChain
from intellibricks.rag.contracts import SupportsContextRetrieval
from intellibricks.rag.schema import ContextSourceSequence, Query
from .tools import SupportsCallableConversion

if TYPE_CHECKING:
    from fastapi import APIRouter, FastAPI
    from Litestar import Litestar
    from litestar.handlers import HTTPRouteHandler


type AgentInput = Sequence[MessageType]


class AgentMetadata(TypedDict):
    """
    Agent metadata is a typed dictionary used to store general
    or additional metadata about an agent.
    """

    name: str
    description: str


class AgentResponse[S: msgspec.Struct = RawResponse](
    msgspec.Struct, frozen=True, kw_only=True
):
    """
    A structured response that all agents will return from their `run` or `run_async` methods.

    Using msgspec.Struct ensures fast, typed serialization.
    """

    agent: Agent[S]
    """The agent that generated this response."""

    content: ChatCompletion[S]
    """Detailed information about the contents of the Agent completion. Including the contents, metadata, usage, id, etc."""

    tool_calls: Sequence[ToolCall] = msgspec.field(default_factory=list)

    @property
    def text(self) -> str:
        """
        A convenience property that returns the text of the response.
        """
        return self.content.text

    @property
    def parsed(self) -> S:
        return self.content.parsed

    def to_llm_described_text(self) -> str:
        """
        A convenience method that returns the text of the response,
        with the agent's name and description prepended.
        """
        agent_name = self.agent.metadata["name"]
        agent_description = self.agent.metadata["description"]
        response_text = self.text

        return (
            f"<|agent_info|>\n"
            f"Name: {agent_name}\n"
            f"Description: {agent_description}\n"
            f"<|end_agent_info|>\n\n"
            f"<|response|>\n"
            f"{response_text}\n"
            f"<|end_response|>"
        )


class Agent[S: msgspec.Struct = RawResponse](msgspec.Struct, frozen=True, kw_only=True):
    task: Annotated[
        str,
        msgspec.Meta(
            title="Task",
            description="The task this agent performs.",
            examples=["Financial Analysis"],
        ),
    ]

    instructions: Annotated[
        Sequence[str],
        msgspec.Meta(
            title="Instructions",
            description="The instructions on how the agent might perform the task.",
            examples=[
                [
                    "Analyze the financial data and provide insights.",
                ]
            ],
        ),
    ]

    synapse: Annotated[
        Synapse | SynapticFallbackChain,
        msgspec.Meta(
            title="Synapse",
            description="The synapse to use for the agent.",
        ),
    ]

    tool_synapse: Annotated[
        Optional[Synapse | SynapticFallbackChain],
        msgspec.Meta(
            title="Tool Synapse",
            description="The synapse to use for the tools.",
        ),
    ] = msgspec.field(default=None)

    metadata: Annotated[
        AgentMetadata,
        msgspec.Meta(
            title="Metadata",
            description="Metadata about the agent.",
            examples=[
                {
                    "name": "Financial Analyst",
                    "description": "An agent that analyzes financial data.",
                }
            ],
        ),
    ]

    response_model: Annotated[
        type[S],
        msgspec.Meta(
            title="Response Model",
            description="The response model the agenrt should return.",
        ),
    ] = msgspec.field(default_factory=lambda: cast(type[S], RawResponse()))

    generation_config: Annotated[
        GenerationConfig,
        msgspec.Meta(
            title="Generation Config",
            description="The generation configuration for the agent.",
        ),
    ] = msgspec.field(default_factory=GenerationConfig)

    tools: Annotated[
        Sequence[Callable[..., Any] | SupportsCallableConversion],
        msgspec.Meta(title="Tools", description="Tools that the agent can call"),
    ] = msgspec.field(default_factory=list)

    context_sources: Annotated[
        Sequence[SupportsContextRetrieval],
        msgspec.Meta(
            title="Context Stores",
            description="A sequence of context stores to retrieve additional context from.",
        ),
    ] = msgspec.field(default_factory=list)

    @property
    def fastapi_router(self) -> APIRouter:
        return self.to_fastapi_async_router(
            f"/agents/{self.metadata['name'].lower()}/completions", "post"
        )

    @property
    def fastapi_app(self) -> FastAPI:
        return self.to_fastapi_async_app(
            f"/agents/{self.metadata['name'].lower()}/completions", "post"
        )

    @property
    def litestar_route_handler(self) -> HTTPRouteHandler:
        return self.to_litestar_async_route_handler(
            f"/agents/{self.metadata['name'].lower()}/completions", "post"
        )

    @property
    def litestar_app(self) -> Litestar:
        return self.to_litestar_async_app(
            f"/agents/{self.metadata['name'].lower()}/completions", "post"
        )

    def run(
        self, inp: str | AgentInput, trace_params: Optional[TraceParams] = None
    ) -> AgentResponse[S]:
        """
        Public synchronous method for running this agent.
        Under the hood, it delegates to `_before_run`, `_run_logic`, `_after_run`,
        and wraps `_run_async` if needed.

        1) Pre-run steps
        2) `run_async` call
        3) Post-run steps
        """
        _input = [UserMessage.from_text(inp)] if isinstance(inp, str) else inp

        self._before_run(_input, trace_params=trace_params)
        response = self._run_logic(_input, trace_params=trace_params)
        self._after_run(_input, response, trace_params=trace_params)
        return response

    async def run_async(
        self, inp: str | AgentInput, trace_params: Optional[TraceParams] = None
    ) -> AgentResponse[S]:
        """
        Public asynchronous entry-point.
        Applies the template method pattern in async form:

        1) Pre-run steps
        2) `run_logic_async`
        3) Post-run steps
        """
        _input = [UserMessage.from_text(inp)] if isinstance(inp, str) else inp
        await self._before_run_async(_input, trace_params=trace_params)
        response = await self._run_logic_async(_input, trace_params=trace_params)
        await self._after_run_async(_input, response, trace_params=trace_params)
        return response

    @ensure_module_installed("fastapi", "fastapi")
    def to_fastapi_async_router(
        self, prefix: str, method: Literal["get", "post", "delete", "put"]
    ) -> APIRouter:  # TODO: add more parameters
        from fastapi import APIRouter

        def transform_data(data: list[dict[str, Any]]) -> AgentInput:
            return [MessageFactory.create_from_dict(item) for item in data]

        def enc_hook(obj: Any) -> Any:
            """
            Custom encoding hook for msgspec.
            Converts unsupported types (like Maybe) into serializable formats.
            """
            if isinstance(obj, Maybe):
                return obj.unwrap()
            elif isinstance(obj, type) and issubclass(obj, msgspec.Struct):
                return {}
            elif callable(obj):
                # Serialize the function's reference
                func_info = {
                    "type": "function",
                    "name": obj.__name__,
                }
                return func_info
            else:
                print(obj)
                raise TypeError(f"Cannot serialize object of type {type(obj)}")

        router = APIRouter(prefix=prefix)

        match method:
            case "get":

                @router.get("/")
                async def _(data: list[dict[str, Any]]) -> dict[str, Any]:
                    agent_response = await self.run_async(transform_data(data))
                    encoded_response = msgspec.json.encode(
                        agent_response, enc_hook=enc_hook
                    )
                    return msgspec.json.decode(encoded_response, type=dict)
            case "post":

                @router.post("/")
                async def _(data: list[dict[str, Any]]) -> dict[str, Any]:
                    agent_response = await self.run_async(transform_data(data))
                    print(agent_response)
                    encoded_response = msgspec.json.encode(
                        agent_response, enc_hook=enc_hook
                    )
                    return msgspec.json.decode(encoded_response, type=dict)
            case "delete":

                @router.delete("/")
                async def _(data: list[dict[str, Any]]) -> dict[str, Any]:
                    agent_response = await self.run_async(transform_data(data))
                    encoded_response = msgspec.json.encode(
                        agent_response, enc_hook=enc_hook
                    )
                    return msgspec.json.decode(encoded_response, type=dict)
            case "put":

                @router.put("/")
                async def _(data: list[dict[str, Any]]) -> dict[str, Any]:
                    agent_response = await self.run_async(transform_data(data))
                    encoded_response = msgspec.json.encode(
                        agent_response, enc_hook=enc_hook
                    )
                    return msgspec.json.decode(encoded_response, type=dict)

        return router

    @ensure_module_installed("fastapi", "fastapi")
    def to_fastapi_async_app(
        self,
        router_prefix: str,
        method: Optional[Literal["get", "post", "delete", "put"]] = None,
    ) -> FastAPI:
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(
            self.to_fastapi_async_router(prefix=router_prefix, method=method or "post"),
        )
        return app

    @ensure_module_installed("litestar", "litestar")
    def to_litestar_async_route_handler(
        self, prefix: str, method: Literal["get", "post", "delete", "put"]
    ) -> HTTPRouteHandler:
        from litestar import delete, get, post, put

        match method:
            case "get":

                @get(prefix)
                async def handler(data: AgentInput) -> AgentResponse[S]:
                    agent_response = await self.run_async(data)
                    return agent_response
            case "post":

                @post(prefix)
                async def handler(data: AgentInput) -> AgentResponse[S]:
                    agent_response = await self.run_async(data)
                    return agent_response
            case "delete":

                @delete(prefix)
                async def handler(data: AgentInput) -> AgentResponse[S]:
                    agent_response = await self.run_async(data)
                    return agent_response
            case "put":

                @put(prefix)
                async def handler(data: AgentInput) -> AgentResponse[S]:
                    agent_response = await self.run_async(data)
                    return agent_response

        return handler

    @ensure_module_installed("litestar", "litestar")
    def to_litestar_async_app(
        self,
        route_handler_prefix: str,
        method: Optional[Literal["get", "post", "delete", "put"]] = None,
    ) -> Litestar:
        from litestar import Litestar

        def enc_hook(obj: Any) -> Any:
            """
            Custom encoding hook for msgspec.
            Converts unsupported types (like Maybe) into serializable formats.
            """
            if isinstance(obj, Maybe):
                return obj.unwrap()
            elif isinstance(obj, type) and issubclass(obj, msgspec.Struct):
                return {}
            elif callable(obj):
                # Serialize the function's reference
                func_info = {
                    "type": "function",
                    "name": obj.__name__,
                }
                return func_info
            else:
                print(obj)
                raise TypeError(f"Cannot serialize object of type {type(obj)}")

        app = Litestar(
            route_handlers=[
                self.to_litestar_async_route_handler(
                    route_handler_prefix, method or "post"
                )
            ],
            type_encoders={self.response_model: enc_hook},
        )

        return app

    def _run_logic(
        self, inp: AgentInput, trace_params: Optional[TraceParams] = None
    ) -> AgentResponse[S]:
        return run_sync(self._run_logic_async, inp)

    def _before_run(
        self, inp: Sequence[Message], trace_params: Optional[TraceParams] = None
    ) -> None:
        pass

    def _after_run(
        self,
        inp: Sequence[Message],
        response: AgentResponse[S],
        trace_params: Optional[TraceParams] = None,
    ) -> None:
        pass

    async def _before_run_async(
        self, inp: Sequence[Message], trace_params: Optional[TraceParams] = None
    ) -> None:
        pass

    async def _after_run_async(
        self,
        inp: Sequence[Message],
        response: AgentResponse[S],
        trace_params: Optional[TraceParams] = None,
    ) -> None:
        pass

    async def _run_logic_async(
        self, inp: AgentInput, trace_params: Optional[TraceParams] = None
    ) -> AgentResponse[S]:
        message_sequence = MessageSequence(inp)
        context_sequence: ContextSourceSequence = ContextSourceSequence(
            [
                await store.retrieve_context_async(
                    query=Query.from_text(message_sequence.full_llm_described_text)
                )
                for store in self.context_sources
            ]
        )

        context_raw_text = context_sequence.full_text
        developer_prompt = (
            "AGENT ROLE:"
            "You are an advanced AI agent named {name}\n\n"
            "PRIMARY OBJECTIVE:\n"
            "{task}\n\n"
            "AGENT DESCRIPTION:"
            "{description}.\n\n"
            "Your instructions are: {instructions}.\n"
            "{context}"
        ).format(
            name=self.metadata["name"],
            task=self.task,
            description=self.metadata["description"],
            instructions="".join(self.instructions),
            context=f"The following context was provided by context sources: {context_raw_text}"
            if context_raw_text
            else "",
        )

        # Try to find any instance of DeveloperMessage in the input, if present, raise an error
        if any(isinstance(message, DeveloperMessage) for message in inp):
            raise ValueError(
                "DeveloperMessage is not allowed in the input to the agent."
            )

        messages: Sequence[Message] = list(
            chain([DeveloperMessage.from_text(developer_prompt)], inp)
        )

        agent_has_tools: bool = bool(self.tools)
        tool_call_sequence: ToolCallSequence = ToolCallSequence([])
        if agent_has_tools:
            final_tools: Sequence[Callable[..., Any]] = [
                tool.to_callable()
                if isinstance(tool, SupportsCallableConversion)
                else tool
                for tool in self.tools
            ]

            tool_synapse = self.tool_synapse or self.synapse
            tool_completion = await tool_synapse.chat_async(
                messages,
                tools=final_tools,
                n=self.generation_config.n,
                temperature=self.generation_config.temperature,
                max_tokens=self.generation_config.max_tokens,
                max_retries=self.generation_config.max_retries,
                top_p=self.generation_config.top_p,
                top_k=self.generation_config.top_k,
                stop_sequences=self.generation_config.stop_sequences,
                cache_config=self.generation_config.cache_config,
                trace_params=trace_params or self.generation_config.trace_params,
                general_web_search=self.generation_config.general_web_search,
                language=self.generation_config.language,
                timeout=self.generation_config.timeout,
            )
            tool_call_sequence = tool_completion.tool_calls

        tool_message_sequence = tool_call_sequence.to_tool_message_sequence()
        all_messages_sequence: MessageSequence = MessageSequence(
            messages
        ) + MessageSequence(tool_message_sequence)

        final_completion = await self.synapse.chat_async(
            all_messages_sequence.messages,
            response_model=self.response_model or None,
            n=self.generation_config.n,
            temperature=self.generation_config.temperature,
            max_tokens=self.generation_config.max_tokens,
            max_retries=self.generation_config.max_retries,
            top_p=self.generation_config.top_p,
            top_k=self.generation_config.top_k,
            stop_sequences=self.generation_config.stop_sequences,
            cache_config=self.generation_config.cache_config,
            trace_params=trace_params or self.generation_config.trace_params,
            general_web_search=self.generation_config.general_web_search,
            language=self.generation_config.language,
            timeout=self.generation_config.timeout,
        )

        return AgentResponse(
            agent=self,
            content=cast(ChatCompletion[S], final_completion),
            tool_calls=tool_call_sequence.sequence,
        )


class DirectorAgent[S: msgspec.Struct = RawResponse](Agent[S], frozen=True):
    actors: Sequence[Agent[S]]

    async def _run_logic_async(
        self, inp: Sequence[Message], trace_params: Optional[TraceParams] = None
    ) -> AgentResponse[S]:
        raise NotImplementedError("TODO")
