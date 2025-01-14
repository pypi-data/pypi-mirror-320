import json,os
from gai.lib.common.http_utils import http_post
from gai.lib.common.generators_utils import chat_string_to_list
from gai.lib.common.errors import ApiException
from gai.lib.common.logging import getLogger
logger = getLogger(__name__)
from gai.lib.config.config_utils import get_client_config

from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat_model import ChatModel
from openai import OpenAI
from typing import get_args,Union, Optional,Callable

# This class is used by the monkey patch to override the openai's chat.completions.create() function.
# This is also the class responsible for for GAI's text-to-text completion.
# The main driver is the create() function that can be used to generate or stream completions as JSON output.
# The output from create() should be indisguishable from the output of openai's chat.completions.create() function.
#
# Example:
# from openai import OpenAI
# client = OpenAI()
# from gai.ttt.client.completions import Completions
# client = Completions.PatchOpenAI(client)
# client.chat.completions.create(model="exllamav2-mistral7b",messages=[{"role":"user","content":"Tell me a one sentence story"}])

class Completions:

    def __init__(self):
        self.output = None

    @staticmethod
    # override_get_client_from_model is meant to be used for unit testing
    def PatchOpenAI(openai_client:OpenAI, override_get_client_from_model:Optional[Callable]=None):

        # Save the original openai.completions.create function
        openai_create = openai_client.chat.completions.create

        # Replace openai.completions.create with a wrapper over the original create function
        def patched_create(**kwargs):
            
            # The model is required to determine the client type patched to the openai_client so it should be determined first.
            model = kwargs.get("model", None)
            if not model:
                raise Exception("completions.patched_create: Model not provided")

            # Retrieve the corresponding client configuration from the model, or raise an exception if it is not found.
            if override_get_client_from_model:
                client_config = override_get_client_from_model(model)
            else:
                client_config = get_client_config(config_type_or_name=model)
            
            """
            This is a convenient function for extracting the content of the response object.
            Example:
            - For generation.
            use `response.extract()` instead of using `response.choices[0].message.content`.
            - For stream.
                for chunk in response:
                    if chunk:
                        chunk.extract()
            """
            def attach_extractor(response,is_stream):

                if not is_stream:
                    # return message content
                    if response.choices[0].message.content:
                        response.extract = lambda: {
                            "type":"content",
                            "content": response.choices[0].message.content
                        }
                        return response
                    # return message toolcall
                    if response.choices[0].message.tool_calls:
                        response.extract = lambda: {
                            "type":"function",
                            "name": response.choices[0].message.tool_calls[0].function.name,
                            "arguments": response.choices[0].message.tool_calls[0].function.arguments
                        }
                        return response
                    raise Exception("completions.attach_extractor: Response is neither content nor toolcall. Please verify the API response.")
                
                def streamer():

                    for chunk in response:

                        if chunk.choices[0].delta.content or chunk.choices[0].delta.role:
                            chunk.extract = lambda: chunk.choices[0].delta.content

                        if chunk.choices[0].delta.tool_calls:

                            if chunk.choices[0].delta.tool_calls[0].function.name:
                                chunk.extract = lambda: {
                                    "type":"function",
                                    "name": chunk.choices[0].delta.tool_calls[0].function.name,
                                }

                            if chunk.choices[0].delta.tool_calls[0].function.arguments:
                                chunk.extract = lambda: {
                                    "type":"function",
                                    "arguments": chunk.choices[0].delta.tool_calls[0].function.arguments,
                                }

                        if chunk.choices[0].finish_reason:
                            chunk.extract = lambda: {
                                "type":"finish_reason",
                                "finish_reason": chunk.choices[0].finish_reason
                            }

                        if not chunk.extract:
                            raise Exception(f"completions.streamer: Chunk response contains unexpected data that cannot be processed. chunk: {chunk.__dict__}")
                        yield chunk

                return (chunk for chunk in streamer())            
            
            if client_config and client_config.client_type == "gai":
                
                url = client_config.url
                
                # "messages": required
                messages=kwargs.get("messages")

                # "stream"
                stream=kwargs.get("stream",None)

                # "tools": array of tool call objects
                tools=kwargs.get("tools",None)

                # "max_tokens": 
                max_tokens=kwargs.pop("max_tokens",None)

                # "temperature"
                temperature=kwargs.get("temperature",None)

                # "top_p"
                top_p=kwargs.get("top_p",None)

                # "top_k"
                top_k=kwargs.get("top_k",None)

                # "json_schema"
                json_schema=kwargs.get("json_schema",None)

                # "tool_choice"
                tool_choice=kwargs.get("tool_choice","auto")

                # "stop_conditions"
                stop=kwargs.get("stop",None)

                # "timeout"
                timeout=kwargs.get("timeout",30.0)

                response = Completions()._create(
                    url=url,
                    messages=messages, 
                    stream=stream, 
                    tools=tools, 
                    max_tokens = max_tokens,
                    temperature=temperature, 
                    top_p=top_p, 
                    top_k=top_k, 
                    json_schema=json_schema, 
                    tool_choice=tool_choice,
                    stop=stop,
                    timeout=timeout)
                
                response = attach_extractor(response,stream)
                return response
            
            # If the model is an openai model, route to openai's chat.completions.create() function.            
            if client_config and client_config.client_type == "openai" and client_config.model in get_args(ChatModel):
                stream=kwargs.get("stream",False)
                response = openai_create(**kwargs)
                response = attach_extractor(response,stream)
                return response
            
            raise Exception(f"completions.patched_create: Model {model} not found in config")

        openai_client.chat.completions.create = patched_create    
        return openai_client    

    # Generate non stream dictionary response for easier unit testing
    def _generate_dict(self, **kwargs):
        response=None
        url = kwargs.pop("url")
        timeout = kwargs.pop("timeout",30.0)
        try:
            response = http_post(url, data={**kwargs},timeout=timeout)
            jsoned=response.json()
            completion = ChatCompletion(**jsoned)
        except ApiException as he:
                raise he
        except Exception as e:
            logger.error(f"completions._generate_dict: error={e} response={response}")
            raise e

        return completion

    # Generate streamed dictionary response for easier unit testing
    def _stream_dict(self, **kwargs):
        response=None
        url = kwargs.pop("url")
        timeout = kwargs.pop("timeout",30.0)
        try:
            response = http_post(url, data={**kwargs},timeout=timeout)
        except ApiException as he:
                raise he
        except Exception as e:
            logger.error(f"completions._stream_dict: error={e}")
            raise e

        for chunk in response.iter_lines():
            try:
                chunk = chunk.decode("utf-8")
                if type(chunk)==str:
                    yield ChatCompletionChunk(**json.loads(chunk))
            except Exception as e:
                # Report the error and continue
                logger.error(f"completions._stream_dict: error={e}")
                pass


    """
    Description:
    This function is a monkey patch for openai's chat.completions.create() function.
    It will override the default completions.create() function to call the local llm instead of gpt-4.
    Example:
    openai_client.chat.completions.create = create
    """
    def _create(self, url:str, messages:list, stream:bool, max_tokens:int, temperature:float=None, top_p:float=None, top_k:float=None, json_schema:dict=None, tools:list=None, tool_choice:str=None, stop:list=None,timeout:float=30.0):

        # Prepare messages
        if not messages:
            raise Exception("Messages not provided")
        if isinstance(messages, str):
            messages = chat_string_to_list(messages)
        if messages[-1]["role"] != "assistant":
            messages.append({"role": "assistant", "content": ""})

        # Prepare payload
        kwargs = {
            "url": url,
            "messages": messages,
            "stream": stream,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "json_schema": json_schema,
            "tools": tools,
            "tool_choice": tool_choice,
            "stop": stop,
            "timeout":timeout
        }
        if not stream:
            response = self._generate_dict(**kwargs)
            return response
        return (chunk for chunk in self._stream_dict(**kwargs))


