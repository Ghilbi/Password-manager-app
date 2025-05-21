import os
import base64
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class EncryptionHandler:
    def __init__(self):
        self.backend = default_backend()
    
    def generate_key(self, password, salt=None):
        """Generate encryption key from password"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        
        key = kdf.derive(password.encode())
        return key, salt
    
    def encrypt_data(self, data, password):
        """Encrypt the data using the provided password"""
        # Generate a key from the password
        key, salt = self.generate_key(password)
        
        # Generate a random IV
        iv = os.urandom(16)
        
        # Create an encryptor
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        # Encrypt the data
        encrypted_data = encryptor.update(data.encode()) + encryptor.finalize()
        
        # Return the encrypted data, salt and IV
        return base64.b64encode(salt + iv + encrypted_data).decode('utf-8')
    
    def decrypt_data(self, encrypted_data, password):
        """Decrypt the data using the provided password"""
        try:
            # Handle possible encoding issues gracefully
            try:
                # Decode the base64 data
                raw_data = base64.b64decode(encrypted_data.encode('utf-8'))
            except UnicodeError:
                # If we hit a UnicodeError, the file might be corrupted or not properly encoded
                raw_data = base64.b64decode(encrypted_data)
            except Exception:
                # For any other base64 decoding error
                return None
                
            # Check if we have enough data for salt, iv and actual content
            if len(raw_data) < 33:  # Minimum size: 16 (salt) + 16 (iv) + 1 (data)
                return None
                
            # Extract the salt and IV
            salt = raw_data[:16]
            iv = raw_data[16:32]
            ciphertext = raw_data[32:]
            
            # Generate the key from the password and salt
            key, _ = self.generate_key(password, salt)
            
            # Create a decryptor
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            
            # Decrypt the data
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Try to decode the result
            try:
                result = decrypted_data.decode('utf-8')
                
                # Validate JSON format
                json.loads(result)
                return result
            except (UnicodeError, json.JSONDecodeError):
                # If we can't decode as UTF-8 or it's not valid JSON, 
                # the password was probably wrong
                return None
                
        except Exception as e:
            print(f"Decryption error: {e}")
            return None 