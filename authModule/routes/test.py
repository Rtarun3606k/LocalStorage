from flask import Blueprint , jsonify  


test_bp = Blueprint('test', __name__)


@test_bp.route('/test', methods=['GET'])
def test_route():
    return  jsonify({"message": "Test route is working!"}), 200


