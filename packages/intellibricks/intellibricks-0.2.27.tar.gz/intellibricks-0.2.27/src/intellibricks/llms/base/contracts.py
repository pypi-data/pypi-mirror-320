from __future__ import annotations

# NOTE: use case of __future__ annotations
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
    runtime_checkable,
)
from architecture.utils import run_sync
import msgspec

from intellibricks.llms.schema import (
    DeveloperMessage,
    Part,
    PartType,
    Prompt,
    RawResponse,
    UserMessage,
)

if TYPE_CHECKING:
    from intellibricks.llms.schema import ChatCompletion, Message

S = TypeVar("S", bound=msgspec.Struct, default=RawResponse)


@runtime_checkable
class SupportsAsyncChat(Protocol):
    async def chat_async(
        self,
        messages: Sequence[Message],
        *,
        response_model: Optional[type[S]] = None,
        n: Optional[int] = None,
        temperature: Optional[float] = None,
        max_completion_tokens: Optional[int] = None,
        max_retries: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[Sequence[str]] = None,
        tools: Optional[Sequence[Callable[..., Any]]] = None,
        timeout: Optional[float] = None,
    ) -> ChatCompletion[S] | ChatCompletion[RawResponse]: ...

    def chat(
        self,
        messages: Sequence[Message],
        *,
        response_model: Optional[type[S]] = None,
        n: Optional[int] = None,
        temperature: Optional[float] = None,
        max_completion_tokens: Optional[int] = None,
        max_retries: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[Sequence[str]] = None,
        tools: Optional[Sequence[Callable[..., Any]]] = None,
        timeout: Optional[float] = None,
    ) -> ChatCompletion[S] | ChatCompletion[RawResponse]:
        return run_sync(
            self.chat_async,
            messages,
            response_model=response_model,
            n=n,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            max_retries=max_retries,
            top_p=top_p,
            top_k=top_k,
            stop_sequences=stop_sequences,
            tools=tools,
            timeout=timeout,
        )

    def complete(
        self,
        prompt: str | Prompt | PartType | Sequence[PartType],
        *,
        system_prompt: Optional[str | Prompt | PartType | Sequence[PartType]] = None,
        response_model: Optional[type[S]] = None,
        n: Optional[int] = None,
        temperature: Optional[float] = None,
        max_completion_tokens: Optional[int] = None,
        max_retries: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[Sequence[str]] = None,
        tools: Optional[Sequence[Callable[..., Any]]] = None,
        timeout: Optional[float] = None,
    ) -> ChatCompletion[S] | ChatCompletion[RawResponse]:
        if system_prompt is None:
            system_prompt = [
                Part.from_text(
                    "You are a helpful assistant."
                    "Answer in the same language"
                    "the conversation goes."
                )
            ]

        match system_prompt:
            case str():
                system_message = DeveloperMessage(
                    contents=[Part.from_text(system_prompt)]
                )
            case Prompt():
                system_message = DeveloperMessage(
                    contents=[Part.from_text(system_prompt.as_string())]
                )
            case Part():
                system_message = DeveloperMessage(contents=[system_prompt])
            case _:
                system_message = DeveloperMessage(contents=system_prompt)

        match prompt:
            case str():
                user_message = UserMessage(contents=[Part.from_text(prompt)])
            case Prompt():
                user_message = UserMessage(
                    contents=[Part.from_text(prompt.as_string())]
                )
            case Part():
                user_message = UserMessage(contents=[prompt])
            case _:
                user_message = UserMessage(contents=prompt)

        messages: Sequence[Message] = [
            system_message,
            user_message,
        ]

        return self.chat(
            messages,
            response_model=response_model,
            n=n,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            max_retries=max_retries,
            top_p=top_p,
            top_k=top_k,
            stop_sequences=stop_sequences,
            tools=tools,
            timeout=timeout,
        )
