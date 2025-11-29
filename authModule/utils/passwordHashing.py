from argon2 import PasswordHasher  

ph = PasswordHasher( time_cost=3,       # iterations 
memory_cost=65536, # 64 MB RAM
parallelism=2,     # CPU threads
hash_len=32,       # output hash size
salt_len=16        # random salt size
)

def hashPassword(password):
    try:
        if not isinstance(password, str) or len(password) == 0:
            print(ValueError("Password must be a non-empty string."))
            return None
        hashed_password = ph.hash(password)
        return hashed_password
    except Exception as e:
        print(f"Error hashing password: {e}")
        return None 




def verifyPassword(stored_hash, provided_password):
    try:
        ph.verify(stored_hash, provided_password)
        return True
    except Exception as e:
        print(f"Password verification failed: {e}")
        return False

