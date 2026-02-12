from cryptography.fernet import Fernet 
import os 
def load_or_generate_key(): 
    if not os.path.exists("secret.key"): 
        key = Fernet.generate_key() 
        with open("secret.key","wb") as key_file: 
            key_file.write(key) 
    return open("secret.key","rb").read() 

def encrypt_data(data): 
    # Works for both strings (encoded) and bytes (images) 
    key = load_or_generate_key() 
    f = Fernet(key) 
    return f.encrypt(data if isinstance(data, bytes) else data.encoded()) 

def decrypt_data(encrypted_data): 
    key = load_or_generate_key() 
    f = Fernet(key) 
    return f.decrypt(encrypted_data) 
