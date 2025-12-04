
import base64
from functools import wraps
from flask import request, jsonify
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from encryption.loadKeys import load_private_key


def rsa_decrypt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        # 1. Extract from JSON
        if request.is_json:
            encrypted_data = request.json.get("encrypted_data")
            print( "encrypted data:", encrypted_data)
            key_id = request.json.get("key_id")

        # 2. Extract from form-data (multipart/form-data)
        elif request.content_type and "multipart/form-data" in request.content_type:
            encrypted_data = request.form.get("encrypted_data")
            key_id = request.form.get("key_id")

        # 3. Extract from x-www-form-urlencoded
        elif request.content_type and "application/x-www-form-urlencoded" in request.content_type:
            encrypted_data = request.form.get("encrypted_data")
            key_id = request.form.get("key_id")

        else:
            return jsonify({"error": "Unsupported content type"}), 400

        if not encrypted_data or not key_id:
            return jsonify({"error": "encrypted_data and key_id required"}), 400

        # Decode base64 ciphertext
        try:
            ciphertext = base64.b64decode(encrypted_data)
        except Exception:
            return jsonify({"error": "Invalid base64 encrypted_data"}), 400

        # Load private key
        try:
            private_key = load_private_key(key_id)
        except Exception:
            return jsonify({"error": "Invalid key_id"}), 400

        # Decrypt
        try:
            decrypted_bytes = private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                )
            )
            decrypted_text = decrypted_bytes.decode()
            print("Decrypted text:", decrypted_text)
        except Exception:
            return jsonify({"error": "Decryption failed"}), 401

        # Inject decrypted data
        request.decrypted_text = decrypted_text
        return func(*args, **kwargs)

    return wrapper

