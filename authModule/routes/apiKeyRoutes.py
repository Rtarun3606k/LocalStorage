from flask import Blueprint, request, jsonify
from app import db, log, limiter
from database.apiKey import ApiKey
from database.services import ServicesModel
from database.userServices import UserService
from database.UserModel import UserModel
from utils.passwordHashing import hashPassword, ph
from sqlalchemy.exc import IntegrityError
import secrets
import datetime

apiKeyRoute = Blueprint('apiKeyRoute', __name__)


@apiKeyRoute.route('/health', methods=['GET'])
def apikey_health():
    """Health check endpoint for API key routes"""
    return jsonify({"status": "API Key route is healthy"}), 200


@apiKeyRoute.errorhandler(Exception)
def handle_apikey_route_error(e):
    log.error(f"Error in apiKeyRoute: {str(e)}")
    return jsonify({"error": "An error occurred in apiKeyRoute"}), 500


@apiKeyRoute.route('/generate', methods=['POST'])
@limiter.limit("5 per hour")
def generate_api_key():
    """
    Generate an API key for a user to access a specific service
    Expected JSON payload:
    {
        "userId": "user-uuid",
        "serviceId": "service-uuid",
        "scopes": ["read", "write"],  # optional
        "expiresInDays": 30  # optional, default 30 days
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('userId')
        service_id = data.get('serviceId')
        scopes = data.get('scopes', ["read", "write"])
        expires_in_days = data.get('expiresInDays', 30)

        # Validation
        if not user_id or not service_id:
            log.warning("Missing userId or serviceId", extra={
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            return jsonify({"error": "userId and serviceId are required"}), 400

        # Verify user exists
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            log.warning("User not found", extra={
                "user_id": user_id,
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            return jsonify({"error": "User not found"}), 404

        # Verify service exists
        service = ServicesModel.query.filter_by(id=service_id).first()
        if not service:
            log.warning("Service not found", extra={
                "service_id": service_id,
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            return jsonify({"error": "Service not found"}), 404

        # Verify user is assigned to this service
        user_service = UserService.query.filter_by(
            user_id=user_id,
            service_id=service_id,
            enabled=True
        ).first()

        if not user_service:
            log.warning("User not assigned to service", extra={
                "user_id": user_id,
                "service_id": service_id,
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            return jsonify({"error": "User is not assigned to this service"}), 403

        # Generate API key (secure random string)
        raw_api_key = secrets.token_urlsafe(32)
        
        # Hash the API key before storing
        hashed_key = hashPassword(raw_api_key)

        # Calculate expiration
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=expires_in_days)

        # Create API key record
        new_api_key = ApiKey(
            user_id=user_id,
            service_id=service_id,
            hashed_key=hashed_key,
            role=user_service.role,
            scopes=scopes,
            expires_at=expires_at,
            revoked=False
        )

        db.session.add(new_api_key)
        db.session.commit()

        log.info(f"API key generated for user {user.email} and service {service.name}", extra={
            "user_id": str(user_id),
            "service_id": str(service_id),
            "api_key_id": str(new_api_key.id),
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })

        return jsonify({
            "message": "API key generated successfully",
            "apiKey": raw_api_key,  # Only returned once!
            "apiKeyId": str(new_api_key.id),
            "serviceName": service.name,
            "scopes": scopes,
            "expiresAt": expires_at.isoformat(),
            "warning": "Store this API key securely. It will not be shown again."
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        log.error(f"Database integrity error: {str(e)}", extra={
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        return jsonify({"error": "Database integrity error"}), 400
    except Exception as e:
        db.session.rollback()
        log.error(f"Error generating API key: {str(e)}", extra={
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        return jsonify({"error": "An error occurred while generating API key"}), 500


@apiKeyRoute.route('/list', methods=['GET'])
@limiter.limit("30 per minute")
def list_api_keys():
    """
    List API keys for a user
    Query parameter: userId
    """
    try:
        user_id = request.args.get('userId')

        if not user_id:
            return jsonify({"error": "userId query parameter is required"}), 400

        # Verify user exists
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get all API keys for this user
        api_keys = ApiKey.query.filter_by(user_id=user_id).all()

        api_keys_list = [{
            "id": str(api_key.id),
            "serviceId": str(api_key.service_id),
            "serviceName": api_key.service.name,
            "role": api_key.role,
            "scopes": api_key.scopes,
            "revoked": api_key.revoked,
            "expiresAt": api_key.expires_at.isoformat() if api_key.expires_at else None,
            "createdAt": api_key.created_at.isoformat() if api_key.created_at else None,
            "isExpired": api_key.expires_at < datetime.datetime.utcnow() if api_key.expires_at else False
        } for api_key in api_keys]

        log.info(f"Listed {len(api_keys_list)} API keys for user {user.email}", extra={
            "user_id": str(user_id),
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })

        return jsonify({
            "apiKeys": api_keys_list,
            "count": len(api_keys_list)
        }), 200

    except Exception as e:
        log.error(f"Error listing API keys: {str(e)}", extra={
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        return jsonify({"error": "An error occurred while listing API keys"}), 500


@apiKeyRoute.route('/revoke/<api_key_id>', methods=['POST'])
@limiter.limit("10 per hour")
def revoke_api_key(api_key_id):
    """Revoke an API key"""
    try:
        api_key = ApiKey.query.filter_by(id=api_key_id).first()
        
        if not api_key:
            log.warning("API key not found", extra={
                "api_key_id": api_key_id,
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            return jsonify({"error": "API key not found"}), 404

        api_key.revoked = True
        db.session.commit()

        log.info(f"API key revoked", extra={
            "api_key_id": str(api_key_id),
            "user_id": str(api_key.user_id),
            "service_id": str(api_key.service_id),
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })

        return jsonify({
            "message": "API key revoked successfully",
            "apiKeyId": str(api_key.id)
        }), 200

    except Exception as e:
        db.session.rollback()
        log.error(f"Error revoking API key: {str(e)}", extra={
            "api_key_id": api_key_id,
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        return jsonify({"error": "An error occurred while revoking API key"}), 500


@apiKeyRoute.route('/validate', methods=['POST'])
@limiter.limit("100 per minute")
def validate_api_key():
    """
    Validate an API key
    Expected JSON payload or Header:
    {
        "apiKey": "raw-api-key-string"
    }
    OR
    Header: Authorization: Bearer <api-key>
    """
    try:
        # Try to get API key from JSON body
        data = request.get_json() or {}
        raw_api_key = data.get('apiKey')
        
        # If not in body, try Authorization header
        if not raw_api_key:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                raw_api_key = auth_header.split(' ')[1]

        if not raw_api_key:
            return jsonify({
                "valid": False,
                "error": "API key is required in body or Authorization header"
            }), 400

        # Get all non-revoked API keys
        api_keys = ApiKey.query.filter_by(revoked=False).all()

        # Try to match the provided key with stored hashed keys
        matched_key = None
        for api_key in api_keys:
            try:
                # Verify the raw key against stored hash
                from utils.passwordHashing import verifyPassword
                if verifyPassword(api_key.hashed_key, raw_api_key):
                    matched_key = api_key
                    break
            except:
                continue

        if not matched_key:
            log.warning("Invalid API key provided", extra={
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            return jsonify({
                "valid": False,
                "error": "Invalid API key"
            }), 401

        # Check if expired
        if matched_key.expires_at and matched_key.expires_at < datetime.datetime.utcnow():
            log.warning("Expired API key used", extra={
                "api_key_id": str(matched_key.id),
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            return jsonify({
                "valid": False,
                "error": "API key has expired"
            }), 401

        # Return validation success with metadata
        return jsonify({
            "valid": True,
            "apiKeyId": str(matched_key.id),
            "userId": str(matched_key.user_id),
            "serviceId": str(matched_key.service_id),
            "serviceName": matched_key.service.name,
            "role": matched_key.role,
            "scopes": matched_key.scopes,
            "userEmail": matched_key.user.email,
            "userName": matched_key.user.name
        }), 200

    except Exception as e:
        log.error(f"Error validating API key: {str(e)}", extra={
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        return jsonify({
            "valid": False,
            "error": "An error occurred while validating API key"
        }), 500
