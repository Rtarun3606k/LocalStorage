from flask import Blueprint, request, jsonify
from app import db, log, limiter
from database.services import ServicesModel
from database.organization import OrganizationModel
from database.userServices import UserService
from database.UserModel import UserModel
from sqlalchemy.exc import IntegrityError

serviceRoute = Blueprint('serviceRoute', __name__)


@serviceRoute.route('/health', methods=['GET'])
def service_health():
    """Health check endpoint for service routes"""
    return jsonify({"status": "Service route is healthy"}), 200


@serviceRoute.errorhandler(Exception)
def handle_service_route_error(e):
    log.error(f"Error in serviceRoute: {str(e)}")
    return jsonify({"error": "An error occurred in serviceRoute"}), 500


@serviceRoute.route('/create', methods=['POST'])
@limiter.limit("10 per hour")
def create_service():
    """
    Create a new service
    Expected JSON payload:
    {
        "name": "StorageEngine",
        "description": "File storage and management service",
        "role": "User",
        "organizationId": "uuid-string"
    }
    """
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        role = data.get('role', 'User')
        organization_id = data.get('organizationId')

        # Validation
        if not name:
            log.warning("Missing service name", extra={
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            return jsonify({"error": "Service name is required"}), 400

        if not organization_id:
            log.warning("Missing organization ID", extra={
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            return jsonify({"error": "Organization ID is required"}), 400

        # Verify organization exists
        organization = OrganizationModel.query.filter_by(id=organization_id).first()
        if not organization:
            log.warning("Organization not found", extra={
                "organization_id": organization_id,
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            return jsonify({"error": "Organization not found"}), 404

        # Check if service already exists for this organization
        existing_service = ServicesModel.query.filter_by(
            name=name,
            organizationId=organization_id
        ).first()
        
        if existing_service:
            log.warning("Service already exists", extra={
                "service_name": name,
                "organization_id": organization_id,
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            return jsonify({
                "error": "Service with this name already exists for this organization",
                "service_id": str(existing_service.id)
            }), 409

        # Create new service
        from database.services import UserRoleEnum
        
        # Convert string role to enum
        try:
            role_enum = UserRoleEnum[role]
        except KeyError:
            role_enum = UserRoleEnum.User

        new_service = ServicesModel(
            name=name,
            description=description,
            role=role_enum,
            organizationId=organization_id
        )

        db.session.add(new_service)
        db.session.commit()

        log.info(f"Service {name} created successfully", extra={
            "service_name": name,
            "service_id": str(new_service.id),
            "organization_id": organization_id,
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })

        return jsonify({
            "message": f"Service {name} created successfully",
            "service_id": str(new_service.id),
            "name": new_service.name,
            "description": new_service.description,
            "role": new_service.role.value
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
        log.error(f"Error creating service: {str(e)}", extra={
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        return jsonify({"error": "An error occurred while creating the service"}), 500


@serviceRoute.route('/list', methods=['GET'])
@limiter.limit("30 per minute")
def list_services():
    """
    List all services
    Optional query parameter: organizationId
    """
    try:
        organization_id = request.args.get('organizationId')

        if organization_id:
            services = ServicesModel.query.filter_by(organizationId=organization_id).all()
        else:
            services = ServicesModel.query.all()

        services_list = [{
            "id": str(service.id),
            "name": service.name,
            "description": service.description,
            "role": service.role.value,
            "organizationId": str(service.organizationId),
            "createdAt": service.createdAt,
            "updatedAt": service.updatedAt
        } for service in services]

        log.info(f"Listed {len(services_list)} services", extra={
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })

        return jsonify({
            "services": services_list,
            "count": len(services_list)
        }), 200

    except Exception as e:
        log.error(f"Error listing services: {str(e)}", extra={
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        return jsonify({"error": "An error occurred while listing services"}), 500


@serviceRoute.route('/<service_id>', methods=['GET'])
@limiter.limit("30 per minute")
def get_service(service_id):
    """Get a specific service by ID"""
    try:
        service = ServicesModel.query.filter_by(id=service_id).first()
        
        if not service:
            log.warning("Service not found", extra={
                "service_id": service_id,
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            return jsonify({"error": "Service not found"}), 404

        return jsonify({
            "id": str(service.id),
            "name": service.name,
            "description": service.description,
            "role": service.role.value,
            "organizationId": str(service.organizationId),
            "createdAt": service.createdAt,
            "updatedAt": service.updatedAt
        }), 200

    except Exception as e:
        log.error(f"Error getting service: {str(e)}", extra={
            "service_id": service_id,
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        return jsonify({"error": "An error occurred while getting the service"}), 500


@serviceRoute.route('/assign', methods=['POST'])
@limiter.limit("10 per hour")
def assign_service_to_user():
    """
    Assign a service to a user
    Expected JSON payload:
    {
        "userId": "uuid-string",
        "serviceId": "uuid-string",
        "role": "User"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('userId')
        service_id = data.get('serviceId')
        role = data.get('role', 'User')

        # Validation
        if not user_id or not service_id:
            return jsonify({"error": "userId and serviceId are required"}), 400

        # Verify user exists
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Verify service exists
        service = ServicesModel.query.filter_by(id=service_id).first()
        if not service:
            return jsonify({"error": "Service not found"}), 404

        # Check if already assigned
        existing_assignment = UserService.query.filter_by(
            user_id=user_id,
            service_id=service_id
        ).first()

        if existing_assignment:
            return jsonify({
                "error": "Service already assigned to user",
                "assignment_id": str(existing_assignment.id)
            }), 409

        # Create assignment
        new_assignment = UserService(
            user_id=user_id,
            service_id=service_id,
            role=role,
            enabled=True
        )

        db.session.add(new_assignment)
        db.session.commit()

        log.info(f"Service {service.name} assigned to user {user.email}", extra={
            "user_id": str(user_id),
            "service_id": str(service_id),
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })

        return jsonify({
            "message": "Service assigned to user successfully",
            "assignment_id": str(new_assignment.id)
        }), 201

    except Exception as e:
        db.session.rollback()
        log.error(f"Error assigning service to user: {str(e)}", extra={
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        return jsonify({"error": "An error occurred while assigning the service"}), 500
