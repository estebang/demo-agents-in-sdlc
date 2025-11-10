from flask import jsonify, Response, Blueprint
from models import db, Publisher

# Create a Blueprint for publishers routes
publishers_bp = Blueprint("publishers", __name__)

@publishers_bp.route("/api/publishers", methods=["GET"])
def get_publishers() -> Response:
    """Get all publishers"""
    publishers = Publisher.query.all()
    publishers_list = [publisher.to_dict() for publisher in publishers]
    return jsonify(publishers_list)

