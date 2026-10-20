from cryptography.fernet import Fernet

import os
import configparser

_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '..', 'public', 'public_config.ini')
cfg = configparser.ConfigParser()
cfg.read(_config_path)

#Cryptography key for encrypting and decrypting data
class Crypto:
    #Now use .ini to store the local key
    def __init__(self):
        env_key_path = os.getenv('LAPAGENT_CRYPT_KEY_PATH')
        key_path = env_key_path or cfg.get('database', 'cryp_key_path')
        if os.path.isabs(key_path):
            real_key_path = key_path
        else:
            real_key_path = os.path.normpath(os.path.join(_current_dir, key_path))

        os.makedirs(os.path.dirname(real_key_path), exist_ok=True)
        if not os.path.exists(real_key_path):
            key = Fernet.generate_key()
            with open(real_key_path, 'wb') as key_file:
                key_file.write(key)
        else:
            with open(real_key_path, 'rb') as key_file:
                key = key_file.read() 
        self.cipher = Fernet(key)

    def encode(self, data):
        # Convert the potential string into bytes
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.cipher.encrypt(data).decode('utf-8')

    def decode(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.cipher.decrypt(data).decode('utf-8')