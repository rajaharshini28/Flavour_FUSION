from database.repository import Repository
from collections import Counter

class PersonalizationService:
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()

    def get_implicit_user_profile(self, user_id=1) -> dict:
        """
        Analyzes past searches and recipe interactions to derive implicit user preferences.
        Returns top cuisines, top diets, top ingredients, and interaction count.
        """
        try:
            interactions = self.repo.get_user_interactions(user_id=user_id, limit=50)
            searches = self.repo.get_recent_searches(user_id=user_id, limit=20)
        except Exception:
            interactions = []
            searches = []

        
        cuisines_counter = Counter()
        diets_counter = Counter()
        ingredients_counter = Counter()
        
        for s in searches:
            if s.get('cuisine') and s['cuisine'] != 'Any':
                cuisines_counter[s['cuisine']] += 1
            if s.get('diet') and s['diet'] != 'None':
                diets_counter[s['diet']] += 1
            if s.get('ingredients'):
                for ing in s['ingredients'].split(','):
                    clean_ing = ing.strip().lower()
                    if clean_ing:
                        ingredients_counter[clean_ing] += 1
                        
        return {
            'top_cuisines': [c[0] for c in cuisines_counter.most_common(3)],
            'top_diets': [d[0] for d in diets_counter.most_common(3)],
            'top_ingredients': [i[0] for i in ingredients_counter.most_common(5)],
            'total_interactions': len(interactions) + len(searches)
        }

    def calculate_history_score(self, recipe: dict, recipe_ingredients: list[str], user_profile: dict) -> float:
        """
        Calculates a personalization fit score (0 - 100) based on user's past interaction history.
        """
        if not user_profile or user_profile.get('total_interactions', 0) == 0:
            return 70.0 # Neutral score for new users
            
        score = 50.0
        
        # Check cuisine preference match from history
        recipe_cuisines = recipe.get('cuisines', [])
        for pref_cuisine in user_profile.get('top_cuisines', []):
            if any(pref_cuisine.lower() in c.lower() for c in recipe_cuisines):
                score += 25.0
                break
                
        # Check ingredient preference match from history
        top_ings = set(user_profile.get('top_ingredients', []))
        if top_ings:
            overlap = top_ings.intersection(set(recipe_ingredients))
            if overlap:
                score += min(25.0, len(overlap) * 10.0)
                
        return min(100.0, score)
