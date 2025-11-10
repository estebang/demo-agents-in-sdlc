from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query
from typing import List

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

def get_games_base_query() -> Query:
    return db.session.query(Game).join(
        Publisher, 
        Game.publisher_id == Publisher.id, 
        isouter=True
    ).join(
        Category, 
        Game.category_id == Category.id, 
        isouter=True
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    # Use the base query for all games
    query = get_games_base_query()
    
    # Get filter parameters from query string
    category_ids: List[str] = request.args.getlist('category_id')
    publisher_ids: List[str] = request.args.getlist('publisher_id')
    
    # Apply category filter if provided
    if category_ids:
        # Convert to integers and filter
        category_ids_int = [int(cid) for cid in category_ids if cid.isdigit()]
        if category_ids_int:
            query = query.filter(Game.category_id.in_(category_ids_int))
    
    # Apply publisher filter if provided
    if publisher_ids:
        # Convert to integers and filter
        publisher_ids_int = [int(pid) for pid in publisher_ids if pid.isdigit()]
        if publisher_ids_int:
            query = query.filter(Game.publisher_id.in_(publisher_ids_int))
    
    games_query = query.all()
    
    # Convert the results using the model's to_dict method
    games_list = [game.to_dict() for game in games_query]
    
    return jsonify(games_list)

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)
