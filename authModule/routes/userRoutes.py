from flask import Blueprint, request, jsonify
from flask import Blueprint, request, jsonify
from extensions import db, log, limiter
from utils.passwordHashing import hashPassword, verifyPassword
from database.UserModel import UserModel

from utils.passwordHashing import hashPassword , verifyPassword
from database.UserModel import UserModel 
from utils.kerberosUtils import generate_session_key
from utils.tokenManagement import create_tgt


# print(UserModel.__table__)
userRoute = Blueprint('userRoute', __name__)


# Health check endpoint
@userRoute.route('/health', methods=['GET'])
@limiter.limit("5 per minute")  # Rate limiting: 5 login attempts per minute
def users_health():
    return jsonify({"status": "Users route is healthy"}), 200

#error handler 
@userRoute.errorhandler(Exception)
def handle_user_route_error(e):
    log.error(f"Error in userRoute: {str(e)}")
    return jsonify({"error": "An error occurred in userRoute"}), 500

#register user endpoint
@userRoute.route('/register', methods=['POST'])
@limiter.limit("3 per hour")  # Rate limiting: 3 registration attempts per hour
def register_user():
    username = None
    try:
        #request from client json       
        data = request.get_json()
        username = data.get('username') #name of the user
        email = data.get('email')      #email of the user
        dateOfBirth = data.get('dateOfBirth') #dob of the user
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        # print(f"Received registration data for user: {username}, email: {email}, dateOfBirth: {dateOfBirth} , password: {password} , password_confirm: {password_confirm} ")

        # Basic validation
        if not username or not password or not password_confirm:
            log.warning("Missing username or password in registration", extra={"username": username,"ip": request.remote_addr,"api_endpoint": request.path})
            return jsonify({"error": "Username and password are required"}), 400
       
        # Here you would typically add code to save the user to a database
        if password != password_confirm:
            log.warning("Password and confirmation do not match",  extra={"username": username,"ip": request.remote_addr,"api_endpoint": request.path})

            return jsonify({"error": "Passwords do not match"}), 400
        
        #check if the user already exists
        existing_user = UserModel.query.filter_by(email=email).first()
        if existing_user:
            log.warning("User with this email already exists",  extra={"username": username,"ip": request.remote_addr,"api_endpoint": request.path})
            return jsonify({"error": "User with this email already exists"}), 400
        
       #hash the password before storing 
        hashed_password = hashPassword(password)
        # For this example, we'll just return a success message
        addNewuser = UserModel(name=username,email=email,passwordHash=hashed_password,dataOfBirth=dateOfBirth)
        db.session.add(addNewuser) 
        db.session.commit() 
        #log the registration event    
        log.info(f"User {username} registered successfully",  extra={"username": username,"ip": request.remote_addr,"api_endpoint": request.path})
        return jsonify({"message": f"User {username} registered successfully"}), 201


    except Exception as e:
        db.session.rollback()
        log.error(f"Error registering user: {str(e)}", extra={"username": username,"ip": request.remote_addr,"api_endpoint": request.path})
        return jsonify({"error": "An error occurred during registration"}), 500





# user login endpoint
@userRoute.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limiting: 5 login attempts per minute
def login_user():
    email = None
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            log.warning(
                "Missing email or password in login",
                extra={"email": email, "ip": request.remote_addr, "api_endpoint": request.path}
            )
            return jsonify({"error": "Email and password are required"}), 400

        # Fetch user
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            log.warning(
                "User not found during login",
                extra={"email": email, "ip": request.remote_addr, "api_endpoint": request.path}
            )
            return jsonify({"error": "Invalid email or password"}), 401

        # Verify password
        if not verifyPassword(user.passwordHash, password):
            log.warning(
                "Invalid password during login",
                extra={"email": email, "ip": request.remote_addr, "api_endpoint": request.path}
            )
            return jsonify({"error": "Invalid email or password"}), 401

        # 🔐 Kerberos-style AS logic
        session_key = generate_session_key()
        tgt = create_tgt(str(user.id), session_key)

        log.info(
            "User logged in and TGT issued",
            extra={"email": email, "ip": request.remote_addr, "api_endpoint": request.path}
        )

        return jsonify({
            "message": "Login successful",
            "tgt": tgt
        }), 200

    except Exception as e:
        log.error(
            f"Error during user login: {str(e)}",
            extra={"email": email, "ip": request.remote_addr, "api_endpoint": request.path}
        )
        return jsonify({"error": "An error occurred during login"}), 500