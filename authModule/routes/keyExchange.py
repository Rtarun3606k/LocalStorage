from flask import Blueprint,request, jsonify
from encryption.loadKeys import load_server_public_key
from utils.tokenManagement import validate_tgt, create_service_ticket
from app import log


keyExchange_bp = Blueprint('keyExchange', __name__)

@keyExchange_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify that the key exchange service is running.
    """
    return jsonify({"status": "Key Exchange Service is healthy"}), 200

@keyExchange_bp.route('/public-key', methods=['GET'])
def exchange_key():
    """
    Endpoint to exchange public keys between client and server.
    Expects a JSON payload with 'client_public_key'.
    Returns the server's public key.
    """

    try:
        server_public_key = load_server_public_key() 
        log.info("Server public key loaded successfully for key exchange.", extra={"endpoint": request.path, "method": request.method, "client_ip": request.remote_addr, "status": 200})
        return jsonify({"server_public_key": server_public_key}), 200
    except FileNotFoundError:
        return jsonify({"error": "Server public key not found"}), 500

@keyExchange_bp.route('/tgs', methods=['POST'])
def ticket_granting_service():
    tgt = request.headers.get("X-TGT")
    if not tgt:
        return jsonify({"error": "Missing TGT"}), 401

    service = request.json.get("service")
    if not service:
        return jsonify({"error": "Service name required"}), 400

    tgt_data = validate_tgt(tgt)
    if not tgt_data:
        return jsonify({"error": "Invalid or expired TGT"}), 403

    service_ticket = create_service_ticket(
        user_id=tgt_data["user_id"],
        service=service,
        session_key=tgt_data["session_key"]
    )

    log.info(
        "Service ticket issued",
        extra={"user_id": tgt_data["user_id"], "service": service}
    )

    return jsonify({"service_ticket": service_ticket}), 200
