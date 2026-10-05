def extract_nutrition_data(recipe: dict) -> dict:
    """
    Extracts macronutrients (Calories, Protein, Fat, Carbs) from Spoonacular recipe object.
    Gracefully handles missing or incomplete fields.
    """
    nutrition_obj = recipe.get('nutrition', {})
    nutrients = nutrition_obj.get('nutrients', [])
    
    data = {
        'calories': None,
        'protein': None,
        'fat': None,
        'carbs': None
    }
    
    for item in nutrients:
        name = item.get('name', '').lower()
        amount = item.get('amount')
        if amount is not None:
            if 'calories' in name or 'energy' in name:
                data['calories'] = float(amount)
            elif 'protein' in name:
                data['protein'] = float(amount)
            elif 'fat' in name and 'saturated' not in name:
                data['fat'] = float(amount)
            elif 'carbohydrate' in name:
                data['carbs'] = float(amount)
                
    return data

def calculate_nutrition_score(recipe_nutrition: dict, user_targets: dict) -> float:
    """
    Calculates a nutrition fit score (0 - 100) based on user's macro preferences.
    If no nutritional constraints are specified, defaults to 100.
    """
    max_cal = user_targets.get('max_calories')
    min_prot = user_targets.get('min_protein')
    max_fat = user_targets.get('max_fat')
    max_carbs = user_targets.get('max_carbs')
    
    # If user provided no targets, score is 100
    if max_cal is None and min_prot is None and max_fat is None and max_carbs is None:
        return 100.0
        
    scores = []
    
    # 1. Max Calories check
    cal = recipe_nutrition.get('calories')
    if max_cal is not None:
        if cal is not None:
            if cal <= max_cal:
                scores.append(100.0)
            else:
                # Excess penalty: lose 1% for every 10 calories over limit
                penalty = (cal - max_cal) / 10.0
                scores.append(max(0.0, 100.0 - penalty))
        else:
            scores.append(70.0) # neutral fallback if field missing
            
    # 2. Min Protein check
    prot = recipe_nutrition.get('protein')
    if min_prot is not None:
        if prot is not None:
            if prot >= min_prot:
                scores.append(100.0)
            else:
                # Deficit penalty: lose 3% for every 1g protein under target
                penalty = (min_prot - prot) * 3.0
                scores.append(max(0.0, 100.0 - penalty))
        else:
            scores.append(70.0)
            
    # 3. Max Fat check
    fat = recipe_nutrition.get('fat')
    if max_fat is not None:
        if fat is not None:
            if fat <= max_fat:
                scores.append(100.0)
            else:
                penalty = (fat - max_fat) * 2.5
                scores.append(max(0.0, 100.0 - penalty))
        else:
            scores.append(70.0)
            
    # 4. Max Carbs check
    carbs = recipe_nutrition.get('carbs')
    if max_carbs is not None:
        if carbs is not None:
            if carbs <= max_carbs:
                scores.append(100.0)
            else:
                penalty = (carbs - max_carbs) * 1.5
                scores.append(max(0.0, 100.0 - penalty))
        else:
            scores.append(70.0)
            
    if not scores:
        return 100.0
        
    return sum(scores) / len(scores)
