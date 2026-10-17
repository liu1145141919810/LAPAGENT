from openai import OpenAI

import os
import configparser

from Crypto.cryptography import Crypto
from Agent import base_url_dict

_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '..', 'public', 'public_config.ini')
cfg = configparser.ConfigParser()
cfg.read(_config_path)

class Agent:
    def __init__(self):
        self.crypto=Crypto()
        self.api_model = None  # initialize the model name as None
        try:
            api_key = cfg.get('AIAgent', 'api_key')
            api_key = self.crypto.decode(api_key)
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            pass
    def set_API_key(self, api):
        api_key = api.split(' ')[1] # Extract the actual API key after the prefix
        self.api_model = api.split(' ')[0]  # Extract the model name before the space
        try:
            encrypted_key = self.crypto.encode(api_key)
            self.client = OpenAI(
                api_key=api_key, 
                base_url=base_url_dict.get(self.api_model, "https://api.openai.com/v1")
                )

            with open(os.path.join(_current_dir, '..', 'public', 'public_config.ini'), 'w') as configfile:
                cfg.set('AIAgent', 'api_key', encrypted_key)
                cfg.write(configfile)
                print(f"API key has been set and saved successfully. {api_key}")
        except Exception as e:
            print(f"Error occurred for the provided API key: {e}")
    def set_model(self, model):
        self.api_model = model
        # have a brief try here
        self.interact()
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
            print(f"AI Assistant: {answer}")
            return answer
        except Exception as e:
            print(f"Error during interaction: {e}")
            return f"Error: {str(e)}"
    def get_model_list(self):
        try:
            models = self.client.models.list()
            model_ids = [model.id for model in models.data]
            return model_ids
        except Exception as e:
            print(f"Error retrieving model list: {e}")
            return []