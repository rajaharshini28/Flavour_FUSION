import os
import tempfile
import pytest
from database.db import init_db, get_or_create_default_user
from database.repository import Repository

@pytest.fixture
def temp_repo():
    db_fd, db_path = tempfile.mkstemp()
    init_db(db_path)
    get_or_create_default_user(db_path)
    repo = Repository(db_path)
    yield repo
    os.close(db_fd)
    os.unlink(db_path)

def test_save_and_get_user_preferences(temp_repo):
    prefs = {
        'diet': 'Vegetarian',
        'cuisine': 'Indian',
        'max_calories': 500
    }
    temp_repo.save_user_preferences(user_id=1, prefs=prefs)
    
    saved = temp_repo.get_user_preferences(user_id=1)
    assert saved is not None
    assert saved['diet'] == 'Vegetarian'
    assert saved['cuisine'] == 'Indian'
    assert saved['max_calories'] == 500

def test_save_search_and_recommendations(temp_repo):
    search_params = {
        'ingredients': 'chicken, tomato',
        'diet': 'Gluten Free',
        'cuisine': 'Indian'
    }
    search_id = temp_repo.save_search(user_id=1, search_params=search_params)
    assert search_id is not None
    
    recs = [
        {
            'recipe_id': 101,
            'title': 'Test Chicken Curry',
            'image': 'http://example.com/img.jpg',
            'final_score': 92.5,
            'component_scores': {
                'ingredient_score': 90.0,
                'diet_score': 100.0,
                'nutrition_score': 85.0,
                'cuisine_score': 100.0,
                'time_score': 90.0,
                'history_score': 80.0
            },
            'matched_ingredients': ['chicken', 'tomato'],
            'missing_ingredients': ['onion'],
            'explanation': {'reasons': ['Matches ingredients']}
        }
    ]
    
    temp_repo.save_recommendations(search_id=search_id, recommendations=recs)
    saved_recs = temp_repo.get_recommendations_for_search(search_id=search_id)
    
    assert len(saved_recs) == 1
    assert saved_recs[0]['recipe_name'] == 'Test Chicken Curry'
    assert saved_recs[0]['recommendation_score'] == 92.5
    assert 'chicken' in saved_recs[0]['matched_ingredients']

def test_log_recipe_interaction(temp_repo):
    temp_repo.log_recipe_interaction(user_id=1, recipe_id=101, recipe_name="Test Curry", interaction_type="view")
    interactions = temp_repo.get_user_interactions(user_id=1)
    
    assert len(interactions) == 1
    assert interactions[0]['recipe_name'] == "Test Curry"
    assert interactions[0]['interaction_type'] == "view"
