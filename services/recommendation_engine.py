from config import Config
from services.recipe_processor import extract_recipe_ingredients, match_ingredients
from services.nutrition_processor import extract_nutrition_data, calculate_nutrition_score
from services.personalization_service import PersonalizationService
from utils.normalizers import parse_ingredient_list

class RecommendationEngine:
    def __init__(self, weights=None, personalization_service=None):
        self.weights = weights or {
            'ingredient': Config.INGREDIENT_WEIGHT,
            'diet': Config.DIET_WEIGHT,
            'nutrition': Config.NUTRITION_WEIGHT,
            'cuisine': Config.CUISINE_WEIGHT,
            'time': Config.TIME_WEIGHT,
            'history': Config.HISTORY_WEIGHT
        }
        self.personalization_service = personalization_service or PersonalizationService()

    def process_and_rank_recipes(self, raw_recipes: list[dict], search_params: dict, user_id=1) -> list[dict]:
        """
        Executes the local recommendation pipeline:
        1. User Input Parsing & Normalization
        2. Hard Constraint Filtering (Allergies, Diets, Strict Cooking Time)
        3. Feature Extraction & Multi-criteria Scoring
        4. Implicit History Personalization
        5. Weighted Composite Score Calculation (0-100)
        6. Recipe Ranking & Explainable AI Generation
        """
        user_ingredients = parse_ingredient_list(search_params.get('ingredients', ''))
        user_allergies = parse_ingredient_list(search_params.get('allergies', ''))
        target_diet = (search_params.get('diet') or 'None').strip()
        target_cuisine = (search_params.get('cuisine') or 'Any').strip()
        max_time = search_params.get('max_cooking_time')
        
        user_profile = self.personalization_service.get_implicit_user_profile(user_id=user_id)
        
        scored_recipes = []
        
        for recipe in raw_recipes:
            recipe_ingredients = extract_recipe_ingredients(recipe)
            
            # --- 1. HARD CONSTRAINT FILTERING ---
            # A. Allergy / Excluded ingredient check
            if user_allergies and self._contains_allergies(recipe_ingredients, user_allergies):
                continue
                
            # B. Strict Dietary restriction check
            diet_score, passes_diet_hard_constraint = self._calculate_diet_score(recipe, target_diet)
            if not passes_diet_hard_constraint:
                continue
                
            # C. Strict Cooking Time check (if provided and recipe exceeds it by >20%)
            ready_time = recipe.get('readyInMinutes', 999)
            if max_time and ready_time > (max_time * 1.2):
                continue
                
            # --- 2. SOFT PREFERENCE SCORING ---
            # Component 1: Ingredient Coverage Score (40%)
            ing_match_data = match_ingredients(user_ingredients, recipe_ingredients)
            ingredient_score = ing_match_data['coverage']
            
            # Component 2: Nutrition Fit Score (15%)
            nutrition_data = extract_nutrition_data(recipe)
            nutrition_score = calculate_nutrition_score(nutrition_data, search_params)
            
            # Component 3: Cuisine Match Score (10%)
            cuisine_score = self._calculate_cuisine_score(recipe, target_cuisine)
            
            # Component 4: Cooking Time Fit Score (10%)
            time_score = self._calculate_time_score(ready_time, max_time)
            
            # Component 5: User History Personalization Score (5%)
            history_score = self.personalization_service.calculate_history_score(
                recipe, recipe_ingredients, user_profile
            )
            
            # --- 3. WEIGHTED COMPOSITE SCORE CALCULATION ---
            final_score = (
                (ingredient_score * self.weights['ingredient']) +
                (diet_score * self.weights['diet']) +
                (nutrition_score * self.weights['nutrition']) +
                (cuisine_score * self.weights['cuisine']) +
                (time_score * self.weights['time']) +
                (history_score * self.weights['history'])
            )
            final_score = round(min(100.0, max(0.0, final_score)), 1)
            
            # --- 4. EXPLAINABLE AI RATIONALE GENERATION ---
            explanation = self._generate_explanation(
                recipe=recipe,
                ingredient_data=ing_match_data,
                target_diet=target_diet,
                target_cuisine=target_cuisine,
                ready_time=ready_time,
                max_time=max_time,
                nutrition_data=nutrition_data,
                scores={
                    'ingredient': ingredient_score,
                    'diet': diet_score,
                    'nutrition': nutrition_score,
                    'cuisine': cuisine_score,
                    'time': time_score,
                    'history': history_score,
                    'final': final_score
                }
            )
            
            scored_recipes.append({
                'recipe_id': recipe.get('id'),
                'title': recipe.get('title'),
                'image': recipe.get('image', ''),
                'ready_in_minutes': ready_time,
                'servings': recipe.get('servings', 2),
                'cuisines': recipe.get('cuisines', []),
                'diets': recipe.get('diets', []),
                'matched_ingredients': ing_match_data['matched'],
                'missing_ingredients': ing_match_data['missing'],
                'nutrition': nutrition_data,
                'final_score': final_score,
                'component_scores': {
                    'ingredient_score': round(ingredient_score, 1),
                    'diet_score': round(diet_score, 1),
                    'nutrition_score': round(nutrition_score, 1),
                    'cuisine_score': round(cuisine_score, 1),
                    'time_score': round(time_score, 1),
                    'history_score': round(history_score, 1)
                },
                'explanation': explanation
            })
            
        # --- 5. RANKING ---
        ranked_recipes = sorted(scored_recipes, key=lambda x: x['final_score'], reverse=True)
        return ranked_recipes

    def _contains_allergies(self, recipe_ingredients: list[str], user_allergies: list[str]) -> bool:
        for allergy in user_allergies:
            for req in recipe_ingredients:
                if allergy in req or req in allergy:
                    return True
        return False

    def _calculate_diet_score(self, recipe: dict, target_diet: str) -> tuple[float, bool]:
        if not target_diet or target_diet.lower() == 'none':
            return 100.0, True
            
        recipe_diets = [d.lower() for d in recipe.get('diets', [])]
        target_lower = target_diet.lower()
        
        # Check vegetarian / vegan boolean flags if present
        if target_lower == 'vegetarian' and (recipe.get('vegetarian') or 'vegetarian' in recipe_diets or 'vegan' in recipe_diets):
            return 100.0, True
        if target_lower == 'vegan' and (recipe.get('vegan') or 'vegan' in recipe_diets):
            return 100.0, True
        if target_lower == 'gluten free' and (recipe.get('glutenFree') or 'gluten free' in recipe_diets):
            return 100.0, True
        if target_lower == 'dairy free' and (recipe.get('dairyFree') or 'dairy free' in recipe_diets):
            return 100.0, True
        if target_lower in recipe_diets:
            return 100.0, True
            
        # If strict diet is requested but not satisfied, fail hard constraint
        return 0.0, False

    def _calculate_cuisine_score(self, recipe: dict, target_cuisine: str) -> float:
        if not target_cuisine or target_cuisine.lower() == 'any':
            return 80.0 # Neutral score for unspecified cuisine preference
            
        recipe_cuisines = [c.lower() for c in recipe.get('cuisines', [])]
        target_lower = target_cuisine.lower()
        
        for c in recipe_cuisines:
            if target_lower in c or c in target_lower:
                return 100.0
                
        return 20.0 # Low score if target cuisine mismatch

    def _calculate_time_score(self, ready_time: int, max_time: int) -> float:
        if not max_time:
            return 100.0
        if ready_time <= max_time:
            return 100.0
        # Soft penalty if slightly above target cooking time
        over = ready_time - max_time
        penalty = over * 4.0
        return max(0.0, 100.0 - penalty)

    def _generate_explanation(self, recipe, ingredient_data, target_diet, target_cuisine, ready_time, max_time, nutrition_data, scores) -> dict:
        matched_count = ingredient_data['matched_count']
        req_count = ingredient_data['required_count']
        reasons = []
        
        if req_count > 0:
            reasons.append(f"Matches {matched_count} of {req_count} required ingredients ({round(ingredient_data['coverage'])}% coverage).")
        else:
            reasons.append("Recipe ingredients evaluated.")
            
        if target_diet and target_diet.lower() != 'none':
            reasons.append(f"Meets your {target_diet} dietary constraint.")
            
        if target_cuisine and target_cuisine.lower() != 'any':
            if scores['cuisine'] >= 80:
                reasons.append(f"Matches your preferred {target_cuisine} cuisine.")
            else:
                reasons.append(f"Alternative cuisine option (differs from {target_cuisine}).")
                
        if max_time:
            if ready_time <= max_time:
                reasons.append(f"Fits within your {max_time}-minute cooking time preference (ready in {ready_time} mins).")
            else:
                reasons.append(f"Cooking time is {ready_time} minutes.")
        else:
            reasons.append(f"Ready in {ready_time} minutes.")
            
        if nutrition_data.get('calories') and nutrition_data.get('protein'):
            reasons.append(f"Provides {round(nutrition_data['calories'])} kcal and {round(nutrition_data['protein'])}g protein.")
            
        return {
            'summary': f"Overall Recommendation Score of {round(scores['final'])}%.",
            'reasons': reasons,
            'scores': scores
        }
