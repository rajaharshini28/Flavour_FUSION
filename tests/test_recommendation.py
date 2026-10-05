import pytest
from services.recommendation_engine import RecommendationEngine

@pytest.fixture
def recommendation_engine():
    return RecommendationEngine()

@pytest.fixture
def mock_candidates():
    return [
        {
            "id": 1,
            "title": "High Match Chicken Tikka",
            "readyInMinutes": 25,
            "servings": 4,
            "cuisines": ["Indian"],
            "diets": ["gluten free"],
            "extendedIngredients": [
                {"name": "chicken"},
                {"name": "tomato"},
                {"name": "onion"},
                {"name": "garlic"}
            ],
            "nutrition": {
                "nutrients": [
                    {"name": "Calories", "amount": 450},
                    {"name": "Protein", "amount": 35}
                ]
            }
        },
        {
            "id": 2,
            "title": "Low Match Pasta",
            "readyInMinutes": 45,
            "servings": 2,
            "cuisines": ["Italian"],
            "diets": [],
            "extendedIngredients": [
                {"name": "pasta"},
                {"name": "cheese"},
                {"name": "cream"}
            ],
            "nutrition": {
                "nutrients": [
                    {"name": "Calories", "amount": 800},
                    {"name": "Protein", "amount": 10}
                ]
            }
        },
        {
            "id": 3,
            "title": "Peanut Sauce Chicken",
            "readyInMinutes": 20,
            "servings": 2,
            "cuisines": ["Asian"],
            "diets": ["gluten free"],
            "extendedIngredients": [
                {"name": "chicken"},
                {"name": "peanut butter"}
            ]
        }
    ]

def test_recommendation_scoring_and_ranking(recommendation_engine, mock_candidates):
    search_params = {
        'ingredients': 'chicken, tomato, onion, garlic',
        'diet': 'Gluten Free',
        'cuisine': 'Indian',
        'max_cooking_time': 30
    }
    
    results = recommendation_engine.process_and_rank_recipes(mock_candidates, search_params)
    
    assert len(results) >= 1
    top_recipe = results[0]
    assert top_recipe['recipe_id'] == 1
    assert top_recipe['final_score'] > 75.0
    assert 'matched_ingredients' in top_recipe
    assert 'explanation' in top_recipe

def test_allergy_exclusion_filter(recommendation_engine, mock_candidates):
    search_params = {
        'ingredients': 'chicken',
        'allergies': 'peanut'
    }
    
    results = recommendation_engine.process_and_rank_recipes(mock_candidates, search_params)
    recipe_ids = [r['recipe_id'] for r in results]
    
    # Recipe #3 contains peanut butter and must be filtered out
    assert 3 not in recipe_ids

def test_strict_dietary_filter(recommendation_engine, mock_candidates):
    search_params = {
        'ingredients': 'pasta',
        'diet': 'Gluten Free'
    }
    
    results = recommendation_engine.process_and_rank_recipes(mock_candidates, search_params)
    recipe_ids = [r['recipe_id'] for r in results]
    
    # Recipe #2 does not have gluten free tag and must be filtered out
    assert 2 not in recipe_ids
