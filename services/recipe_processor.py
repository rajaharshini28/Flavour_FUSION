from utils.normalizers import normalize_ingredient, parse_ingredient_list

def extract_recipe_ingredients(recipe: dict) -> list[str]:
    """
    Extracts all ingredient names from a Spoonacular recipe object
    and normalizes them into a list of unique strings.
    """
    ingredients = []
    seen = set()
    
    # Try extendedIngredients first
    ext = recipe.get('extendedIngredients', [])
    for item in ext:
        name = item.get('name') or item.get('cleanName') or item.get('nameClean') or item.get('original')
        if name:
            norm = normalize_ingredient(name)
            if norm and norm not in seen:
                seen.add(norm)
                ingredients.append(norm)
                
    # Also check missedIngredients & usedIngredients if present
    for key in ['usedIngredients', 'missedIngredients', 'unusedIngredients']:
        for item in recipe.get(key, []):
            name = item.get('name') or item.get('cleanName') or item.get('original')
            if name:
                norm = normalize_ingredient(name)
                if norm and norm not in seen:
                    seen.add(norm)
                    ingredients.append(norm)
                    
    return ingredients

def match_ingredients(user_ingredients: list[str], recipe_ingredients: list[str]) -> dict:
    """
    Compares user ingredients with required recipe ingredients.
    Calculates matched ingredients, missing ingredients, and ingredient coverage percentage.
    """
    if not user_ingredients or not recipe_ingredients:
        return {
            'matched': [],
            'missing': recipe_ingredients,
            'coverage': 0.0,
            'matched_count': 0,
            'required_count': len(recipe_ingredients)
        }
        
    user_set = set(user_ingredients)
    matched = []
    missing = []
    
    for req in recipe_ingredients:
        # Check direct or substring match
        is_matched = False
        for u in user_set:
            if u in req or req in u:
                is_matched = True
                break
        if is_matched:
            matched.append(req)
        else:
            missing.append(req)
            
    required_count = len(recipe_ingredients)
    matched_count = len(matched)
    
    coverage = (matched_count / required_count * 100.0) if required_count > 0 else 0.0
    
    return {
        'matched': matched,
        'missing': missing,
        'coverage': min(100.0, max(0.0, coverage)),
        'matched_count': matched_count,
        'required_count': required_count
    }
