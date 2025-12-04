import json
import hashlib

db_file = 'data_user.json'

#hash dari sha256 dari password
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def load_user():
    try:
        with open(db_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    
def simpan_user(user):
    with open(db_file, 'w') as file:
        json.dump(user, file, indent=4)