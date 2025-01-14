from __future__ import annotations
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Type, Sequence

# Try to import the anthropic library.
try:
    from anthropic import AsyncAnthropic  # type: ignore
    from anthropic.types import ToolUseBlock  # type: ignore
    from pydantic import BaseModel  # type: ignore
except ImportError:
    raise ImportError(
        "The anthropic library is required for the AnthropicClient. "
        "Please install it using `pip install anthropic`."
    )
from flexai.llm.client import Client
from flexai.message import (
    AIMessage,
    Message,
    UserMessage,
    SystemMessage,
    ToolCall,
    ToolResult,
    MessageContent,
    TextBlock,
    Usage,
)
from flexai.tool import Tool, TYPE_MAP


ANTHROPIC_BETA_HEADERS = [
    "max-tokens-3-5-sonnet-2024-07-15",
]


def get_tool_call(tool_use: ToolUseBlock) -> ToolCall:
    """Get the tool call from a tool use block.

    Args:
        tool_use: The tool use block to get the call from.

    Returns:
        The tool call from the tool use block.
    """
    return ToolCall(
        id=tool_use.id,
        name=tool_use.name,
        input=tool_use.input,
    )


@dataclass(frozen=True)
class AnthropicClient(Client):
    """Client for interacting with the Anthropic language model."""

    # The client to use for interacting with the model.
    client: AsyncAnthropic = AsyncAnthropic()

    # The model to use for generating responses.
    model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

    # The maximum number of tokens to generate in a response.
    max_tokens: int = 8192

    # Whether to cache messages or not.
    cache_messages: bool = True

    # Extra headers to include in the request.
    extra_headers: dict = field(
        default_factory=lambda: {"anthropic-beta": ",".join(ANTHROPIC_BETA_HEADERS)}
    )

    async def get_chat_response(
        self,
        messages: list[Message],
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        force_tool: bool = True,
    ) -> AIMessage:
        # Send the messages to the model and get the response.
        start = time.time()
        response = await self.client.messages.create(
            **self._get_params(messages, system, tools, force_tool)
        )
        generation_time = time.time() - start

        # Parse out the tool uses from the response.
        tool_uses = [
            get_tool_call(message)
            for message in response.content
            if isinstance(message, ToolUseBlock)
        ]

        # Get the content to return.
        content_to_return = tool_uses or "\n".join(
            [message.text for message in response.content]
        )
        return AIMessage(
            content=content_to_return,
            usage=Usage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                cache_read_tokens=response.usage.cache_read_input_tokens,
                cache_write_tokens=response.usage.cache_creation_input_tokens,
                generation_time=generation_time,
            ),
        )

    async def stream_chat_response(  # type: ignore
        self,
        messages: list[Message],
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
    ) -> AsyncGenerator[str | AIMessage, None]:
        # Initialize variables to store the tool information.
        tool_id = ""
        tool_name = ""
        tool_input_buffer = ""

        # Iterate over the response stream.
        start = time.time()
        response_stream = await self.client.messages.create(
            **self._get_params(messages, system, tools, stream=True)
        )
        usage = Usage()

        async for chunk in response_stream:
            # Add the usage.
            if hasattr(chunk, "message"):
                usage.input_tokens += chunk.message.usage.input_tokens
                usage.output_tokens += chunk.message.usage.output_tokens
                usage.cache_read_tokens += chunk.message.usage.cache_read_input_tokens
                usage.cache_write_tokens += (
                    chunk.message.usage.cache_creation_input_tokens
                )
            if hasattr(chunk, "usage"):
                usage.output_tokens += chunk.usage.output_tokens

            # Tool start block.
            if chunk.type == "content_block_start":
                content = chunk.content_block
                tool_id = content.id
                tool_name = content.name
                # Add the usage.
                yield f"Tool: {tool_name}"  # yield tool name (first chunk)

            # Tool delta.
            elif chunk.type == "content_block_delta":
                tool_input_buffer += chunk.delta.partial_json
                yield chunk.delta.partial_json  # yield chunk of the input

            # Tool stop block.
            elif chunk.type == "message_stop":
                # Parse the tool from the buffer and convert it to a tool call.
                tool_input_dict = (
                    json.loads(tool_input_buffer) if tool_input_buffer else {}
                )
                tool_call = get_tool_call(
                    ToolUseBlock(
                        id=tool_id,
                        name=tool_name,
                        input=tool_input_dict,
                        type="tool_use",
                    )
                )
                usage.generation_time = time.time() - start
                yield AIMessage(
                    content=[tool_call],
                    usage=usage,
                )
                tool_id = tool_name = tool_input_buffer = ""

    def _add_cache_control(self, params: dict) -> dict:
        """Add cache control to the params.

        Args:
            params: The params to add cache control to.

        Returns:
            The params with cache control added.
        """
        if not self.cache_messages:
            return params

        cache_control = {
            "cache_control": {
                "type": "ephemeral",
            }
        }

        # Cache the system message.
        params["system"][0].update(**cache_control)

        # Cache tool definitions.
        if "tools" in params and len(params["tools"]) > 0:
            params["tools"][-1].update(**cache_control)

        # Cache the last two user messages.
        user_idxs = [
            idx
            for idx, message in enumerate(params["messages"])
            if message["role"] == "user"
        ]
        for idx in user_idxs[-2:]:
            message = params["messages"][idx]
            if isinstance(message["content"], str):
                message["content"] = [{"type": "text", "text": message["content"]}]
            message["content"][-1].update(**cache_control)

        return params

    def _get_params(
        self,
        messages: list[Message],
        system: str | SystemMessage,
        tools: list[Tool] | None,
        force_tool: bool = True,
        stream: bool = False,
    ) -> dict:
        """Get the common params to send to the model.

        Args:
            messages: The messages to send to the model.
            system: The system message to send to the model.
            tools: The tools to send to the model.
            force_tool: Whether to force the model to use the tools.
            stream: Whether to stream the response.

        Returns:
            The common params to send to the model.
        """
        # Convert the system prompt to a list of message content.
        if isinstance(system, str):
            system = SystemMessage([TextBlock(text=system)])

        kwargs = {
            "max_tokens": self.max_tokens,
            "messages": self.format_content(messages),
            "model": self.model,
            "system": self.format_content(system.content),
            "extra_headers": self.extra_headers,
        }

        # If tools are provided, force the model to use them (for now).
        if tools:
            kwargs["tools"] = [self.format_tool(tool) for tool in tools]
            if force_tool:
                kwargs["tool_choice"] = {"type": "any"}
        else:
            kwargs["tools"] = []

        if stream:
            kwargs["stream"] = True

        # Add cache control to the params.
        params = self._add_cache_control(kwargs)
        return params

    async def get_structured_response(
        self,
        messages: list[Message],
        model: Type[BaseModel],
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
    ) -> BaseModel:
        """Get the structured response from the chat model.

        Args:
            messages: The messages to send to the model.
            model: The model to use for the response.
            system: Optional system message to set the behavior of the AI.
            tools: Tools to use in the response.

        Returns:
            The structured response from the model.

        Raises:
            ValueError: If the response is not a string.
        """
        schema = model.schema()  # type: ignore
        system = f"""{system}
Return your answer according to the 'properties' of the following schema:
{schema}
Return only the JSON object with the properties filled in.
Do not include anything in your response other than the JSON object.
Do not begin your response with ```json or end it with ```.
"""
        response = await self.get_chat_response(
            messages, system=system, tools=tools, force_tool=False
        )
        response.content = str(response.content)
        content = response.content
        try:
            if not isinstance(content, str):
                raise ValueError("The response is not a string.")
            return model.parse_raw(content)  # type: ignore
        except Exception as e:
            # Try again, printing the exception.
            messages = messages + [
                response,
                UserMessage(
                    content=f"There was an error while parsing. Make sure to only include the JSON. Error: {e}"
                ),
            ]
            return await self.get_structured_response(
                messages, model=model, system=system, tools=tools
            )

    @staticmethod
    def format_tool(tool: Tool) -> dict:
        """Convert the tool to a description.

        Args:
            tool: The tool to format.

        Returns:
            A dictionary describing the tool.
        """
        input_schema = {
            "type": "object",
            "properties": {},
        }
        for param_name, param_type in tool.params:
            param_type = TYPE_MAP.get(str(param_type), param_type)
            input_schema["properties"][param_name] = {
                "type": param_type,
            }

        description = {
            "name": tool.name,
            "description": tool.description,
            "input_schema": input_schema,
        }
        return description

    @classmethod
    def format_content(
        cls,
        value: str
        | Message
        | MessageContent
        | Sequence[MessageContent]
        | Sequence[Message],
    ) -> Any:
        """Format the message content for the Anthropic model.

        Args:
            value: The value to format.

        Returns:
            The formatted message content.

        Raises:
            ValueError: If the message content type is unknown.
        """
        # Base types.
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return [cls.format_content(v) for v in value]

        # Anthropic message format.
        if isinstance(value, Message):
            if isinstance(value.content, ToolCall):
                raise ValueError("Tool calls should not be included in Messages.")
            return {"role": value.role, "content": cls.format_content(value.content)}

        # Message content types.
        if isinstance(value, TextBlock):
            return {
                "type": "text",
                "text": value.text,
            }
        if isinstance(value, ToolCall):
            return {
                "type": "tool_use",
                "id": value.id,
                "name": value.name,
                "input": value.input,
            }
        if isinstance(value, ToolResult):
            return {
                "type": "tool_result",
                "tool_use_id": value.tool_call_id,
                "content": str(value.result),
                "is_error": value.is_error,
            }

        raise ValueError(f"Unknown message content type: {value}")

    @classmethod
    def load_content(
        cls, content: str | list[dict[str, Any]]
    ) -> str | list[MessageContent]:
        """Load the message content from the Anthropic model to dataclasses.

        Args:
            content: The content to load.

        Returns:
            The loaded message content
        """
        # If it's a string, return it.
        if isinstance(content, str):
            return content

        # If it's a list of dictionaries, parse them.
        assert isinstance(content, list)
        parsed_content: list[MessageContent] = []

        for entry in content:
            match entry.pop("type"):
                case "text":
                    parsed_content.append(TextBlock(**entry))
                case "tool_use":
                    parsed_content.append(ToolCall(**entry))
                case "tool_result":
                    parsed_content.append(
                        ToolResult(
                            tool_call_id=entry.pop("tool_use_id"),
                            result=entry.pop("content"),
                            **entry,
                        )
                    )

        return parsed_content
