from flask import Blueprint, request, jsonify, make_response
from app import db, log, limiter
from utils.passwordHashing import hashPassword, verifyPassword
from utils.tokenManagement import create_jwt, create_refresh_token
from database.UserModel import UserModel
import datetime 

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
        # print(f"Received login data for email: {email}, password: {password}")

        if not email or not password:
            log.warning("Missing email or password in login", extra={"email": email,"ip": request.remote_addr,"api_endpoint": request.path})
            return jsonify({"error": "Email and password are required"}), 400

        # Here you would typically verify the user's credentials
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            log.warning("User not found during login", extra={"email": email,"ip": request.remote_addr,"api_endpoint": request.path})
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Verify the password
        if not verifyPassword(user.passwordHash, password):
            log.warning("Invalid password during login", extra={"email": email,"ip": request.remote_addr,"api_endpoint": request.path})
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Generate JWT tokens
        access_token = create_jwt(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        
        # Create response with tokens in cookies
        response = make_response(jsonify({
            "message": f"User {email} logged in successfully",
            "userId": str(user.id),
            "userName": user.name,
            "email": user.email,
            "accessToken": access_token,
            "refreshToken": refresh_token
        }), 200)
        
        # Set cookies with proper security settings
        # Access token cookie (short-lived, 20 minutes)
        response.set_cookie(
            'access_token',
            value=access_token,
            max_age=20 * 60,  # 20 minutes in seconds
            httponly=True,  # Prevents JavaScript access (XSS protection)
            secure=False,  # Set to True in production (HTTPS only)
            samesite='Lax',  # CSRF protection
            path='/'
        )
        
        # Refresh token cookie (long-lived, 14 days)
        response.set_cookie(
            'refresh_token',
            value=refresh_token,
            max_age=14 * 24 * 60 * 60,  # 14 days in seconds
            httponly=True,  # Prevents JavaScript access
            secure=False,  # Set to True in production
            samesite='Lax',
            path='/'
        )
        
        log.info(f"User {email} logged in successfully with JWT tokens", extra={
            "email": email,
            "user_id": str(user.id),
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        
        return response

    except Exception as e:
        log.error(f"Error during user login: {str(e)}", extra={"email": email,"ip": request.remote_addr,"api_endpoint": request.path})
        return jsonify({"error": "An error occurred during login"}), 500


@userRoute.route('/logout', methods=['POST'])
def logout_user():
    """Logout endpoint that clears cookies"""
    try:
        response = make_response(jsonify({
            "message": "Logged out successfully"
        }), 200)
        
        # Clear cookies
        response.set_cookie('access_token', '', max_age=0, path='/')
        response.set_cookie('refresh_token', '', max_age=0, path='/')
        
        log.info("User logged out", extra={
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        
        return response
        
    except Exception as e:
        log.error(f"Error during logout: {str(e)}", extra={
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        return jsonify({"error": "An error occurred during logout"}), 500


@userRoute.route('/refresh', methods=['POST'])
@limiter.limit("10 per hour")
def refresh_access_token():
    """Refresh access token using refresh token from cookie"""
    try:
        # Get refresh token from cookie
        refresh_token = request.cookies.get('refresh_token')
        
        if not refresh_token:
            return jsonify({"error": "Refresh token not found"}), 401
        
        # Verify refresh token
        import jwt
        from app import JWT_REFRESH_SECRET
        
        try:
            payload = jwt.decode(refresh_token, JWT_REFRESH_SECRET, algorithms=["HS256"])
            user_id = payload.get('sub')
            
            # Verify user still exists
            user = UserModel.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Generate new access token
            new_access_token = create_jwt(str(user.id))
            
            response = make_response(jsonify({
                "message": "Access token refreshed",
                "accessToken": new_access_token
            }), 200)
            
            # Set new access token cookie
            response.set_cookie(
                'access_token',
                value=new_access_token,
                max_age=20 * 60,  # 20 minutes
                httponly=True,
                secure=False,  # Set to True in production
                samesite='Lax',
                path='/'
            )
            
            log.info(f"Access token refreshed for user {user.email}", extra={
                "user_id": str(user.id),
                "ip": request.remote_addr,
                "api_endpoint": request.path
            })
            
            return response
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Refresh token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid refresh token"}), 401
        
    except Exception as e:
        log.error(f"Error refreshing token: {str(e)}", extra={
            "ip": request.remote_addr,
            "api_endpoint": request.path
        })
        return jsonify({"error": "An error occurred during token refresh"}), 500
