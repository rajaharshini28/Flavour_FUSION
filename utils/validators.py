def parse_int_safe(val, default=None, min_val=0, max_val=10000):
    """Safely converts input to integer within boundaries."""
    if val is None or val == '':
        return default
    try:
        num = int(val)
        if num < min_val:
            return min_val
        if num > max_val:
            return max_val
        return num
    except (ValueError, TypeError):
        return default

def validate_search_inputs(form_data):
    """
    Validates user search inputs and returns sanitized values along with any error messages.
    """
    errors = []
    
    ingredients_raw = form_data.get('ingredients', '')
    diet = form_data.get('diet', 'None')
    cuisine = form_data.get('cuisine', 'Any')
    meal_type = form_data.get('meal_type', 'Any')
    allergies_raw = form_data.get('allergies', '')
    
    max_calories = parse_int_safe(form_data.get('max_calories'), default=None, min_val=50, max_val=3000)
    min_protein = parse_int_safe(form_data.get('min_protein'), default=None, min_val=0, max_val=200)
    max_fat = parse_int_safe(form_data.get('max_fat'), default=None, min_val=0, max_val=200)
    max_carbs = parse_int_safe(form_data.get('max_carbs'), default=None, min_val=0, max_val=500)
    max_cooking_time = parse_int_safe(form_data.get('max_cooking_time'), default=None, min_val=5, max_val=480)
    
    sanitized = {
        'ingredients': ingredients_raw,
        'diet': diet,
        'cuisine': cuisine,
        'meal_type': meal_type,
        'allergies': allergies_raw,
        'max_calories': max_calories,
        'min_protein': min_protein,
        'max_fat': max_fat,
        'max_carbs': max_carbs,
        'max_cooking_time': max_cooking_time
    }
    
    return sanitized, errors
