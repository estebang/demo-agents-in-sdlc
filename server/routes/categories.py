from flask import jsonify, Response, Blueprint
from models import db, Category

# Create a Blueprint for categories routes
categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/api/categories', methods=['GET'])
def get_categories() -> Response:
    """Get all categories"""
    categories = Category.query.all()
    categories_list = [category.to_dict() for category in categories]
    return jsonify(categories_list)
