from cryptography.fernet import Fernet

import os
import configparser

_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '..', 'public', 'public_configuration.ini')
cfg = configparser.ConfigParser()
cfg.read(_config_path)

#Cryptography key for encrypting and decrypting data
class Crypto:
    #Now use .ini to store the local key
    def __init__(self):
        key_path = cfg.get('database', 'cryp_key_path')
        real_key_path = os.path.normpath(os.path.join(_current_dir, key_path))
        if not os.path.exists(real_key_path):
            key = Fernet.generate_key()
            with open(real_key_path, 'wb') as key_file:
                key_file.write(key)
                key_file.close()
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