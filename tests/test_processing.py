from utils.normalizers import normalize_ingredient, parse_ingredient_list
from services.recipe_processor import match_ingredients
from services.nutrition_processor import calculate_nutrition_score, extract_nutrition_data

def test_ingredient_normalization():
    assert normalize_ingredient("  CHICKEN BREASTS! ") == "chicken breast"
    assert normalize_ingredient("Tomatoes,") == "tomato"
    assert normalize_ingredient("") == ""

def test_parse_ingredient_list():
    raw_input = "Chicken, Tomato , onion, garlic, chicken, TOMATO "
    parsed = parse_ingredient_list(raw_input)
    assert len(parsed) == 4
    assert "chicken" in parsed
    assert "tomato" in parsed
    assert "onion" in parsed
    assert "garlic" in parsed

def test_match_ingredients():
    user_ings = ["chicken", "tomato", "onion", "garlic"]
    recipe_ings = ["chicken breast", "tomato puree", "onion", "garlic", "cream"]
    
    match_data = match_ingredients(user_ings, recipe_ings)
    
    assert match_data['matched_count'] == 4
    assert match_data['required_count'] == 5
    assert match_data['coverage'] == 80.0
    assert "cream" in match_data['missing']

def test_nutrition_scoring():
    recipe = {
        "nutrition": {
            "nutrients": [
                {"name": "Calories", "amount": 500},
                {"name": "Protein", "amount": 30},
                {"name": "Fat", "amount": 15},
                {"name": "Carbohydrates", "amount": 40}
            ]
        }
    }
    nutr_data = extract_nutrition_data(recipe)
    
    targets = {
        'max_calories': 600,
        'min_protein': 25,
        'max_fat': 20,
        'max_carbs': 50
    }
    
    score = calculate_nutrition_score(nutr_data, targets)
    assert score == 100.0
