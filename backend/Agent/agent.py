from openai import OpenAI

import os
import configparser

from Crypto.cryptography import Crypto
from public.AI_configure import base_url_dict
from public.util import PublicToolKit

from public.logger import setup_logger
logger = setup_logger(__name__)

_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '..', 'public', 'public_config.ini')
cfg = configparser.ConfigParser()
cfg.read(_config_path)

class Agent:
    def __init__(self):
        self.crypto=Crypto()
        self.read_env=PublicToolKit()._read_secret_from_env
        self.api_model = None  # initialize the model name as None
        self.api_provider = None  # initialize the provider name as None
        self.client = None
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
        # have a brief try here
    def interact(self,msg=None):
        try:
            response = self.client.chat.completions.create(
                model=self.api_model,
                messages=[
                    {"role": "system", "content": "你是一个有帮助的 AI 助手。"},
                    {"role": "user", "content": str(msg)}
                ]
            )
            answer = response.choices[0].message.content
            logger.info(f"AI Assistant: {answer}")
            return answer
        except Exception as e:
            logger.error(f"Error during interaction: {e}")
            return f"Error: {str(e)}"
    def get_model_list(self):
        try:
            models = self.client.models.list()
            model_ids = [model.id for model in models.data]
            return model_ids
        except Exception as e:
            logger.error(f"Error retrieving model list: {e}")
            return []