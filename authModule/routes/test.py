from flask import Blueprint , jsonify, request  
from encryption.enc import rsa_decrypt_required
import json


test_bp = Blueprint('test', __name__)


@test_bp.route('/test', methods=['GET'])
def test_route():
    return  jsonify({"message": "Test route is working!"}), 200

@test_bp.route('/enc', methods=['POST'])
@rsa_decrypt_required
def encrypted_route():
    decrypted_text = json.loads(request.decrypted_text)
    print(f"Decrypted text: {decrypted_text}")
    return jsonify({"decrypted_text": decrypted_text}), 200



