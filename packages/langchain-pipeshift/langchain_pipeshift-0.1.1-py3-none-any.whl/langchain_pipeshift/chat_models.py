"""Wrapper around Pipeshift APIs."""

from __future__ import annotations

import logging
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    Union,
)

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import (
    BaseChatModel,
    generate_from_stream,
)
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    ChatMessage,
    ChatMessageChunk,
    FunctionMessageChunk,
    HumanMessage,
    HumanMessageChunk,
    SystemMessage,
    SystemMessageChunk,
    ToolMessageChunk,
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.utils import from_env, get_pydantic_field_names
from pydantic import ConfigDict, Field, model_validator
from typing_extensions import Self

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"
BASE_URL = "https://api.pipeshift.com/api/v0"


class ChatPipeshift(BaseChatModel):
    r"""ChatPipeshift chat model.
    Setup:
        Install ``langchain-pipeshift`` and set environment variable ``PIPESHIFT_API_KEY``.
        .. code-block:: bash
            pip install -U langchain-pipeshift
            export PIPESHIFT_API_KEY="your-api-key"
    Key init args — completion params:
        model: str
            Name of model to use.
        temperature: float
            Sampling temperature.
        max_tokens: Optional[int]
            Max number of tokens to generate.
        logprobs: Optional[bool]
            Whether to return logprobs.
    Key init args — client params:
        timeout: Union[float, Tuple[float, float], Any, None]
            Timeout for requests.
        max_retries: int
            Max number of retries.
        api_key: Optional[str]
            Pipeshift API key. If not passed in will be read from env var PIPESHIFT_API_KEY.
    Instantiate:
        .. code-block:: python
            from langhcain_pipeshift import ChatPipeshift
            llm = ChatPipeshift(
                model="meta-llama/Llama-3-70b-chat-hf",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                # api_key="...",
                # other params...
            )
    Invoke:
        .. code-block:: python
            messages = [
                (
                    "system",
                    "You are a helpful translator. Translate the user sentence to French.",
                ),
                ("human", "I love programming."),
            ]
            llm.invoke(messages)
        .. code-block:: python
            AIMessage(
                content="J'adore la programmation.",
                response_metadata={
                    'token_usage': {'completion_tokens': 9, 'prompt_tokens': 32, 'total_tokens': 41},
                    'model_name': 'meta-llama/Llama-3-70b-chat-hf',
                    'system_fingerprint': None,
                    'finish_reason': 'stop',
                    'logprobs': None
                },
                id='run-168dceca-3b8b-4283-94e3-4c739dbc1525-0',
                usage_metadata={'input_tokens': 32, 'output_tokens': 9, 'total_tokens': 41})
    Stream:
        .. code-block:: python
            for chunk in llm.stream(messages):
                print(chunk)
        .. code-block:: python
            content='J' id='run-1bc996b5-293f-4114-96a1-e0f755c05eb9'
            content="'" id='run-1bc996b5-293f-4114-96a1-e0f755c05eb9'
            content='ad' id='run-1bc996b5-293f-4114-96a1-e0f755c05eb9'
            content='ore' id='run-1bc996b5-293f-4114-96a1-e0f755c05eb9'
            content=' la' id='run-1bc996b5-293f-4114-96a1-e0f755c05eb9'
            content=' programm' id='run-1bc996b5-293f-4114-96a1-e0f755c05eb9'
            content='ation' id='run-1bc996b5-293f-4114-96a1-e0f755c05eb9'
            content='.' id='run-1bc996b5-293f-4114-96a1-e0f755c05eb9'
            content='' response_metadata={'finish_reason': 'stop', 'model_name': 'meta-llama/Llama-3-70b-chat-hf'} id='run-1bc996b5-293f-4114-96a1-e0f755c05eb9'
    Async:
        .. code-block:: python
            await llm.ainvoke(messages)
            # stream:
            # async for chunk in (await llm.astream(messages))
            # batch:
            # await llm.abatch([messages])
        .. code-block:: python
            AIMessage(
                content="J'adore la programmation.",
                response_metadata={
                    'token_usage': {'completion_tokens': 9, 'prompt_tokens': 32, 'total_tokens': 41},
                    'model_name': 'meta-llama/Llama-3-70b-chat-hf',
                    'system_fingerprint': None,
                    'finish_reason': 'stop',
                    'logprobs': None
                },
                id='run-09371a11-7f72-4c53-8e7c-9de5c238b34c-0',
                usage_metadata={'input_tokens': 32, 'output_tokens': 9, 'total_tokens': 41})
    Tool calling:
        .. code-block:: python
            from pydantic import BaseModel, Field
            # Only certain models support tool calling, check the pipeshift's website to confirm compatibility
            llm = ChatPipeshift(model="mistralai/Mixtral-8x7B-Instruct-v0.1")
            class GetWeather(BaseModel):
                '''Get the current weather in a given location'''
                location: str = Field(
                    ..., description="The city and state, e.g. San Francisco, CA"
                )
            class GetPopulation(BaseModel):
                '''Get the current population in a given location'''
                location: str = Field(
                    ..., description="The city and state, e.g. San Francisco, CA"
                )
            llm_with_tools = llm.bind_tools([GetWeather, GetPopulation])
            ai_msg = llm_with_tools.invoke(
                "Which city is bigger: LA or NY?"
            )
            ai_msg.tool_calls
        .. code-block:: python
            [
                {
                    'name': 'GetPopulation',
                    'args': {'location': 'NY'},
                    'id': 'call_m5tstyn2004pre9bfuxvom8x',
                    'type': 'tool_call'
                },
                {
                    'name': 'GetPopulation',
                    'args': {'location': 'LA'},
                    'id': 'call_0vjgq455gq1av5sp9eb1pw6a',
                    'type': 'tool_call'
                }
            ]
    Structured output:
        .. code-block:: python
            from typing import Optional
            from pydantic import BaseModel, Field
            class Joke(BaseModel):
                '''Joke to tell user.'''
                setup: str = Field(description="The setup of the joke")
                punchline: str = Field(description="The punchline to the joke")
                rating: Optional[int] = Field(description="How funny the joke is, from 1 to 10")
            structured_llm = llm.with_structured_output(Joke)
            structured_llm.invoke("Tell me a joke about cats")
        .. code-block:: python
            Joke(
                setup='Why was the cat sitting on the computer?',
                punchline='To keep an eye on the mouse!',
                rating=7
            )
    JSON mode:
        .. code-block:: python
            json_llm = llm.bind(response_format={"type": "json_object"})
            ai_msg = json_llm.invoke(
                "Return a JSON object with key 'random_ints' and a value of 10 random ints in [0-99]"
            )
            ai_msg.content
        .. code-block:: python
            ' {\\n"random_ints": [\\n13,\\n54,\\n78,\\n45,\\n67,\\n90,\\n11,\\n29,\\n84,\\n33\\n]\\n}'
    Token usage:
        .. code-block:: python
            ai_msg = llm.invoke(messages)
            ai_msg.usage_metadata
        .. code-block:: python
            {'input_tokens': 37, 'output_tokens': 6, 'total_tokens': 43}
    Logprobs:
        .. code-block:: python
            logprobs_llm = llm.bind(logprobs=True)
            messages=[("human","Say Hello World! Do not return anything else.")]
            ai_msg = logprobs_llm.invoke(messages)
            ai_msg.response_metadata["logprobs"]
        .. code-block:: python
            {
                'content': None,
                'token_ids': [22557, 3304, 28808, 2],
                'tokens': [' Hello', ' World', '!', '</s>'],
                'token_logprobs': [-4.7683716e-06, -5.9604645e-07, 0, -0.057373047]
            }
    Response metadata
        .. code-block:: python
            ai_msg = llm.invoke(messages)
            ai_msg.response_metadata
        .. code-block:: python
            {
                'token_usage': {
                    'completion_tokens': 4,
                    'prompt_tokens': 19,
                    'total_tokens': 23
                    },
                'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
                'system_fingerprint': None,
                'finish_reason': 'eos',
                'logprobs': None
            }
    """  # noqa: E501

    client: Any = None  #: :meta private:
    model: str = DEFAULT_MODEL
    """Model name."""
    temperature: float = 0.7
    """What sampling temperature to use."""
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Holds any model parameters valid for `create` call not explicitly specified."""
    pipeshift_api_key: Optional[str] = Field(
        default_factory=from_env("PIPESHIFT_API_KEY", default=None), alias="api_key"
    )
    request_timeout: Optional[Union[float, Tuple[float, float]]] = Field(
        None, alias="timeout"
    )
    """Timeout for requests to Pipeshift Chat completion API. Default is None."""
    max_retries: int = 6
    """Maximum number of retries to make when generating."""
    streaming: bool = False
    """Whether to stream the results or not."""
    max_tokens: Optional[int] = None
    """Maximum number of tokens to generate."""

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @property
    def lc_secrets(self) -> Dict[str, str]:
        return {"pipeshift_api_key": "PIPESHIFT_API_KEY"}

    @model_validator(mode="before")
    @classmethod
    def build_extra(cls, values: Dict[str, Any]) -> Any:
        """Build extra kwargs from additional params that were passed in."""
        all_required_field_names = get_pydantic_field_names(cls)
        extra = values.get("model_kwargs", {})
        for field_name in list(values):
            if field_name in extra:
                raise ValueError(f"Found {field_name} supplied twice.")
            if field_name not in all_required_field_names:
                logger.warning(
                    f"""WARNING! {field_name} is not a default parameter.
                    {field_name} was transferred to model_kwargs.
                    Please confirm that {field_name} is what you intended."""
                )
                extra[field_name] = values.pop(field_name)

        invalid_model_kwargs = all_required_field_names.intersection(extra.keys())
        if invalid_model_kwargs:
            raise ValueError(
                f"Parameters {invalid_model_kwargs} should be specified explicitly. "
                f"Instead they were passed in as part of `model_kwargs` parameter."
            )

        values["model_kwargs"] = extra
        return values

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        """Validate that api key and python package exists in environment."""
        try:
            import openai
        except ImportError:
            raise ImportError(
                "Could not import openai python package. "
                "Please install it with `pip install openai`."
            )
        try:
            self.client = openai.OpenAI(
                api_key=self.pipeshift_api_key, base_url=BASE_URL
            )
        except AttributeError:
            raise ValueError(
                "`openai` has no `ChatCompletion` attribute, this is likely "
                "due to an old version of the openai package. Try upgrading it "
                "with `pip install --upgrade openai`."
            )
        return self

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling Pipeshift Chat API."""
        return {
            "request_timeout": self.request_timeout,
            "max_tokens": self.max_tokens,
            "stream": self.streaming,
            "temperature": self.temperature,
            **self.model_kwargs,
        }

    def _convert_message_to_dict(self, message: BaseMessage) -> Dict[str, Any]:
        if isinstance(message, ChatMessage):
            message_dict = {"role": message.role, "content": message.content}
        elif isinstance(message, SystemMessage):
            message_dict = {"role": "system", "content": message.content}
        elif isinstance(message, HumanMessage):
            message_dict = {"role": "user", "content": message.content}
        elif isinstance(message, AIMessage):
            message_dict = {"role": "assistant", "content": message.content}
        else:
            raise TypeError(f"Got unknown type {message}")
        return message_dict

    def _create_message_dicts(
        self, messages: List[BaseMessage], stop: Optional[List[str]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        params = dict(self._invocation_params)
        if stop is not None:
            if "stop" in params:
                raise ValueError("`stop` found in both the input and default params.")
            params["stop"] = stop
        message_dicts = [self._convert_message_to_dict(m) for m in messages]
        return message_dicts, params

    def _convert_delta_to_message_chunk(
        self, _dict: Mapping[str, Any], default_class: Type[BaseMessageChunk]
    ) -> BaseMessageChunk:
        role = _dict.get("role")
        content = _dict.get("content") or ""
        additional_kwargs: Dict = {}
        if _dict.get("function_call"):
            function_call = dict(_dict["function_call"])
            if "name" in function_call and function_call["name"] is None:
                function_call["name"] = ""
            additional_kwargs["function_call"] = function_call
        if _dict.get("tool_calls"):
            additional_kwargs["tool_calls"] = _dict["tool_calls"]

        if role == "user" or default_class == HumanMessageChunk:
            return HumanMessageChunk(content=content)
        elif role == "assistant" or default_class == AIMessageChunk:
            return AIMessageChunk(content=content, additional_kwargs=additional_kwargs)
        elif role == "system" or default_class == SystemMessageChunk:
            return SystemMessageChunk(content=content)
        elif role == "function" or default_class == FunctionMessageChunk:
            return FunctionMessageChunk(content=content, name=_dict["name"])
        elif role == "tool" or default_class == ToolMessageChunk:
            return ToolMessageChunk(content=content, tool_call_id=_dict["tool_call_id"])
        elif role or default_class == ChatMessageChunk:
            return ChatMessageChunk(content=content, role=role)  # type: ignore[arg-type]
        else:
            return default_class(content=content)  # type: ignore[call-arg]

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        default_chunk_class = AIMessageChunk

        if stop:
            params["stop_sequences"] = stop
        stream_resp = self.client.chat.completions.create(
            model=params["model"], messages=message_dicts, stream=True
        )
        for chunk in stream_resp:
            if not isinstance(chunk, dict):
                chunk = chunk.dict()
            if len(chunk["choices"]) == 0:
                continue
            choice = chunk["choices"][0]
            chunk = self._convert_delta_to_message_chunk(
                choice["delta"], default_chunk_class
            )
            finish_reason = choice.get("finish_reason")
            generation_info = (
                dict(finish_reason=finish_reason) if finish_reason is not None else None
            )
            default_chunk_class = chunk.__class__
            chunk = ChatGenerationChunk(message=chunk, generation_info=generation_info)
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)
            yield chunk

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.streaming:
            stream_iter = self._stream(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            if stream_iter:
                return generate_from_stream(stream_iter)
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        response = self.client.chat.completions.create(
            model=params["model"], messages=message_dicts
        )
        message = AIMessage(content=response.choices[0].message.content)
        return ChatResult(generations=[ChatGeneration(message=message)])

    @property
    def _invocation_params(self) -> Mapping[str, Any]:
        """Get the parameters used to invoke the model."""
        client_params: Dict[str, Any] = {
            "api_key": self.pipeshift_api_key,
            "api_base": BASE_URL,
            "model": self.model,
        }
        return {**client_params, **self._default_params}

    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return "pipeshift-chat"
