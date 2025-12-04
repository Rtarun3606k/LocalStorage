from argon2 import PasswordHasher
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import jwt
import datetime
from app import JWT_REFRESH_SECRET , JWT_SECRET


#Password hashing using Argon2
def decrypt_password(private_key, encrypted_password_bytes):
    return private_key.decrypt(
        encrypted_password_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode()


# Password hashing using Argon2
def create_jwt(user_id):
    return jwt.encode(
        {
            "sub": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=20)
        },
        JWT_SECRET,
        algorithm="HS256"
    )

# Password hashing using Argon2d
def create_refresh_token(user_id):
    return jwt.encode(
        {
            "sub": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=14)
        },
        JWT_REFRESH_SECRET,
        algorithm="HS256"
    )





