import os
import logging

class PublicToolKit:
    def __init__(self):
       self.logger = logging.getLogger(__name__)
    def _read_secret_from_env(self,secret_var:str,secret_file_var:str)-> str|None:
        #Reading the variables from the environement
        direct_value = os.getenv(secret_var)
        if direct_value is not None:
            return direct_value.strip()
        file_path = os.getenv(secret_file_var)
        if not file_path:
            return None
        try:
            with open(file_path,'r',encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            self.logger.error(f"Error reading secret from file: {e}")
            return None