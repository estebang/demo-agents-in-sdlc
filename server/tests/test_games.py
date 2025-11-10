import unittest
import json
from typing import Dict, List, Any, Optional
from flask import Flask, Response
from models import Game, Publisher, Category, db
from routes.games import games_bp

class TestGamesRoutes(unittest.TestCase):
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"},
            {"name": "Scrum Masters"}
        ],
        "categories": [
            {"name": "Strategy"},
            {"name": "Card Game"}
        ],
        "games": [
            {
                "title": "Pipeline Panic",
                "description": "Build your DevOps pipeline before chaos ensues",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.5
            },
            {
                "title": "Agile Adventures",
                "description": "Navigate your team through sprints and releases",
                "publisher_index": 1,
                "category_index": 1,
                "star_rating": 4.2
            }
        ]
    }
    
    # API paths
    GAMES_API_PATH: str = '/api/games'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        # Create a fresh Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Register the games blueprint
        self.app.register_blueprint(games_bp)
        
        # Initialize the test client
        self.client = self.app.test_client()
        
        # Initialize in-memory database for testing
        db.init_app(self.app)
        
        # Create tables and seed data
        with self.app.app_context():
            db.create_all()
            self._seed_test_data()

    def tearDown(self) -> None:
        """Clean up test database and ensure proper connection closure"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data"""
        # Create test publishers
        publishers = [
            Publisher(**publisher_data) for publisher_data in self.TEST_DATA["publishers"]
        ]
        db.session.add_all(publishers)
        
        # Create test categories
        categories = [
            Category(**category_data) for category_data in self.TEST_DATA["categories"]
        ]
        db.session.add_all(categories)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create test games
        games = []
        for game_data in self.TEST_DATA["games"]:
            game_dict = game_data.copy()
            publisher_index = game_dict.pop("publisher_index")
            category_index = game_dict.pop("category_index")
            
            games.append(Game(
                **game_dict,
                publisher=publishers[publisher_index],
                category=categories[category_index]
            ))
            
        db.session.add_all(games)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data"""
        return json.loads(response.data)

    def test_get_games_success(self) -> None:
        """Test successful retrieval of multiple games"""
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["games"]))
        
        # Verify all games using loop instead of manual testing
        for i, game_data in enumerate(data):
            test_game = self.TEST_DATA["games"][i]
            test_publisher = self.TEST_DATA["publishers"][test_game["publisher_index"]]
            test_category = self.TEST_DATA["categories"][test_game["category_index"]]
            
            self.assertEqual(game_data['title'], test_game["title"])
            self.assertEqual(game_data['publisher']['name'], test_publisher["name"])
            self.assertEqual(game_data['category']['name'], test_category["name"])
            self.assertEqual(game_data['starRating'], test_game["star_rating"])

    def test_get_games_structure(self) -> None:
        """Test the response structure for games"""
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(self.TEST_DATA["games"]))
        
        required_fields = ['id', 'title', 'description', 'publisher', 'category', 'starRating']
        for field in required_fields:
            self.assertIn(field, data[0])

    def test_get_game_by_id_success(self) -> None:
        """Test successful retrieval of a single game by ID"""
        # Get the first game's ID from the list endpoint
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']
        
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/{game_id}')
        data = self._get_response_data(response)
        
        # Assert
        first_game = self.TEST_DATA["games"][0]
        first_publisher = self.TEST_DATA["publishers"][first_game["publisher_index"]]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], first_game["title"])
        self.assertEqual(data['publisher']['name'], first_publisher["name"])
        
    def test_get_game_by_id_not_found(self) -> None:
        """Test retrieval of a non-existent game by ID"""
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/999')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")

    def test_filter_games_by_category(self) -> None:
        """Test filtering games by category ID"""
        # Get the first category's ID
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        category_id = games[0]['category']['id']
        
        # Act - filter by category
        response = self.client.get(f'{self.GAMES_API_PATH}?category_id={category_id}')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data), 0)
        # All returned games should have the specified category
        for game in data:
            self.assertEqual(game['category']['id'], category_id)

    def test_filter_games_by_publisher(self) -> None:
        """Test filtering games by publisher ID"""
        # Get the first publisher's ID
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        publisher_id = games[0]['publisher']['id']
        
        # Act - filter by publisher
        response = self.client.get(f'{self.GAMES_API_PATH}?publisher_id={publisher_id}')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data), 0)
        # All returned games should have the specified publisher
        for game in data:
            self.assertEqual(game['publisher']['id'], publisher_id)

    def test_filter_games_by_multiple_categories(self) -> None:
        """Test filtering games by multiple category IDs"""
        # Get all games to find category IDs
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        
        # Get two different category IDs
        category_ids = list(set([game['category']['id'] for game in games]))
        
        # Act - filter by multiple categories
        category_params = '&'.join([f'category_id={cid}' for cid in category_ids])
        response = self.client.get(f'{self.GAMES_API_PATH}?{category_params}')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(games))  # Should return all games since we're filtering by all categories
        # All returned games should have one of the specified categories
        for game in data:
            self.assertIn(game['category']['id'], category_ids)

    def test_filter_games_by_multiple_publishers(self) -> None:
        """Test filtering games by multiple publisher IDs"""
        # Get all games to find publisher IDs
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        
        # Get two different publisher IDs
        publisher_ids = list(set([game['publisher']['id'] for game in games]))
        
        # Act - filter by multiple publishers
        publisher_params = '&'.join([f'publisher_id={pid}' for pid in publisher_ids])
        response = self.client.get(f'{self.GAMES_API_PATH}?{publisher_params}')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(games))  # Should return all games since we're filtering by all publishers
        # All returned games should have one of the specified publishers
        for game in data:
            self.assertIn(game['publisher']['id'], publisher_ids)

    def test_filter_games_by_category_and_publisher(self) -> None:
        """Test filtering games by both category and publisher"""
        # Get the first game's category and publisher IDs
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        first_game = games[0]
        category_id = first_game['category']['id']
        publisher_id = first_game['publisher']['id']
        
        # Act - filter by both category and publisher
        response = self.client.get(
            f'{self.GAMES_API_PATH}?category_id={category_id}&publisher_id={publisher_id}'
        )
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data), 0)
        # All returned games should have the specified category and publisher
        for game in data:
            self.assertEqual(game['category']['id'], category_id)
            self.assertEqual(game['publisher']['id'], publisher_id)

    def test_filter_games_no_results(self) -> None:
        """Test filtering games with non-existent IDs returns empty list"""
        # Act - filter by non-existent category
        response = self.client.get(f'{self.GAMES_API_PATH}?category_id=999')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 0)

if __name__ == '__main__':
    unittest.main()