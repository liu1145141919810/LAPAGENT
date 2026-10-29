from openai import OpenAI

import os
import configparser
import json
from collections import deque

from Crypto.cryptography import Crypto
from public.AI_configure import base_url_dict
from public.util import PublicToolKit

from public.logger import setup_logger
logger = setup_logger(__name__)

_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '..', 'public', 'public_config.ini')
cfg = configparser.ConfigParser()
cfg.read(_config_path)

from .toolbox import AgentToolBox

class Agent:
    def __init__(self,db):
        self.crypto=Crypto()
        self.read_env=PublicToolKit()._read_secret_from_env
        self.api_model = None  # initialize the model name as None
        self.api_provider = None  # initialize the provider name as None
        self.client = None
        self.maxSoleDepth = 8  # set a default maximum tool call depth
        self.maxConversationDepth = 10  # set a default maximum conversation depth
        self.toolbox = AgentToolBox(db)  # initialize the toolbox instance
        self.messages = deque(maxlen=self.maxConversationDepth)

        self.messages.append(
            [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant."
                },
            ],
        )
        try:
            api_key = self.read_env('LAPAGENT_API_KEY', 'LAPAGENT_API_KEY_FILE')
            if api_key is None:
                logger.info("API key not found in environment variables, reading from config file.")
                api_key = cfg.get('AIAgent', 'api_key')
                api_key = self.crypto.decode(api_key)
            else:
                logger.info("API key found in environment variables.")

            self.api_model = os.getenv('LAPAGENT_API_MODEL')
            if self.api_model is None:
                api_model = cfg.get('AIAgent', 'api_model')
                self.api_model = self.crypto.decode(api_model)

            self.api_provider = os.getenv('LAPAGENT_API_PROVIDER')
            if self.api_provider is None:
                api_provider = cfg.get('AIAgent', 'api_provider')
                self.api_provider = self.crypto.decode(api_provider)
            if not self.api_provider:
                self.api_provider = "openai"  # default to OpenAI if no provider is specified
              
            self.client = OpenAI(
                api_key=api_key,
                base_url=self._resolve_base_url()    
            )
        except Exception as e:
            logger.warning(f"Error occurred during Agent initialization: {e}")

    def _resolve_base_url(self) -> str:
        return os.getenv('LAPAGENT_API_BASE_URL') or base_url_dict.get(
            self.api_provider,
            'https://api.openai.com/v1')

    def set_API_key(self, api):
        parts = api.split(' ', 1)
        if len(parts) != 2:
            logger.error('Invalid API key format. Expected: "provider api_key".')
            return
        api_key = parts[1].strip()  # Extract the actual API key after the prefix
        self.api_provider = parts[0].strip()  # Extract the provider name before the space
        
        try:
            encrypted_key = self.crypto.encode(api_key)
            encrypted_provider = self.crypto.encode(self.api_provider)

            self.client = OpenAI(
                api_key=api_key, 
                base_url=self._resolve_base_url()
                )

            with open(os.path.join(_current_dir, '..', 'public', 'public_config.ini'), 'w') as configfile:
                cfg.set('AIAgent', 'api_key', encrypted_key)
                cfg.set('AIAgent', 'api_provider', encrypted_provider)
                
                cfg.write(configfile)
                logger.info(f"API key has been set and saved successfully")
        except Exception as e:
            logger.error(f"Error occurred for the provided API key: {e}")

    def set_model(self, model):
        self.api_model = model
        model = self.crypto.encode(model)
        with open(os.path.join(_current_dir, '..', 'public', 'public_config.ini'), 'w') as configfile:
            cfg.set('AIAgent', 'api_model', model)
            cfg.write(configfile)
            logger.info(f"Model has been set to {self.api_model} and saved successfully")
    
    def read_model(self):
        return self.api_model

    def read_provider(self):
        return self.api_provider

    def get_model_list(self):
        try:
            models = self.client.models.list()
            model_ids = [model.id for model in models.data]
            return model_ids
        except Exception as e:
            logger.error(f"Error retrieving model list: {e}")
            return []

    def set_tool_conversation_id(self,conversation_id):
        logger.info(f"Setting tool conversation ID to {conversation_id}")
        self.toolbox.backinfo["conversation_id"] = conversation_id
        
    #Following function could be directly used by the users
    def session_interact(self,input):
        input = {"role": "user", "content": input}
        self.messages[-1].append(input)

        msgs = []
        for msg in self.messages:
            msgs.extend(msg)
        msg = self.messages[-1]
        self.messages.append([])
        answer = self.sole_interact(msgs,msg)
        return answer
    
    def sole_interact(self,msgs,current_msg):
        tool_option = "auto"
        try:
            while True:
                if len(current_msg) == self.maxSoleDepth-1:
                    logger.warning("Maximum tool depth reached")
                    tool_option = "none"
                response = self.client.chat.completions.create(
                    model=self.api_model,
                    messages=msgs,
                    tools=self.toolbox.tool_definitions(),
                    tool_choice=tool_option
                )
                tool_calls = response.choices[0].message.tool_calls
                if tool_calls:
                    for call in tool_calls:
                        if len(current_msg) == self.maxSoleDepth-1:
                            break
                        logger.info(f"Tool called: {call}")
                        name = call.function.name
                        arguments = json.loads(call.function.arguments or "{}")
                        result = self.toolbox.call(name, **arguments)
                        logger.info(f"Tool result: {result}")
                        message_pack = {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "name": name,
                            "content": json.dumps(result,default=str)
                        }
                        current_msg.append(message_pack)
                else:
                    answer = response.choices[0].message.content
                    logger.info(f"Answer: {answer}")
                    return answer
        except Exception as e:
            logger.error(f"Error during interaction: {e}")
            return f"Error: {str(e)}"