import requests
import time
import logging
from config import Config

logger = logging.getLogger(__name__)

# Fallback mock dataset for testing or when API key is not configured / quota is exceeded
MOCK_RECIPES = [
    {
        "id": 716429,
        "title": "Butter Chicken (Chicken Tikka Masala)",
        "image": "https://img.spoonacular.com/recipes/716429-312x231.jpg",
        "readyInMinutes": 30,
        "servings": 4,
        "cuisines": ["Indian", "Asian"],
        "diets": ["gluten free"],
        "extendedIngredients": [
            {"name": "chicken", "original": "500g Chicken breast"},
            {"name": "tomato", "original": "2 cups Tomato puree"},
            {"name": "onion", "original": "1 diced Onion"},
            {"name": "garlic", "original": "4 cloves Garlic"},
            {"name": "heavy cream", "original": "1/2 cup Heavy Cream"},
            {"name": "butter", "original": "2 tbsp Butter"}
        ],
        "nutrition": {
            "nutrients": [
                {"name": "Calories", "amount": 540, "unit": "kcal"},
                {"name": "Protein", "amount": 38, "unit": "g"},
                {"name": "Fat", "amount": 32, "unit": "g"},
                {"name": "Carbohydrates", "amount": 18, "unit": "g"}
            ]
        },
        "analyzedInstructions": [{
            "steps": [
                {"number": 1, "step": "Marinate chicken with spices, garlic, and yogurt for 15 mins."},
                {"number": 2, "step": "Saute onions and tomatoes in butter until tender."},
                {"number": 3, "step": "Add chicken and simmer in cream sauce until fully cooked."}
            ]
        }]
    },
    {
        "id": 715538,
        "title": "Rustic Tomato Garlic Pasta",
        "image": "https://img.spoonacular.com/recipes/715538-312x231.jpg",
        "readyInMinutes": 20,
        "servings": 2,
        "cuisines": ["Italian", "Mediterranean"],
        "diets": ["dairy free", "vegan", "vegetarian"],
        "extendedIngredients": [
            {"name": "tomato", "original": "3 ripe Tomatoes"},
            {"name": "garlic", "original": "4 cloves minced Garlic"},
            {"name": "olive oil", "original": "2 tbsp Olive Oil"},
            {"name": "basil", "original": "Fresh Basil leaves"},
            {"name": "pasta", "original": "250g Penne Pasta"}
        ],
        "nutrition": {
            "nutrients": [
                {"name": "Calories", "amount": 420, "unit": "kcal"},
                {"name": "Protein", "amount": 14, "unit": "g"},
                {"name": "Fat", "amount": 12, "unit": "g"},
                {"name": "Carbohydrates", "amount": 65, "unit": "g"}
            ]
        },
        "analyzedInstructions": [{
            "steps": [
                {"number": 1, "step": "Boil pasta in salted water until al dente."},
                {"number": 2, "step": "Saute garlic and tomatoes in olive oil for 5 minutes."},
                {"number": 3, "step": "Toss pasta with sauce and fresh basil leaves."}
            ]
        }]
    },
    {
        "id": 640062,
        "title": "Classic Chicken & Tomato Salad",
        "image": "https://img.spoonacular.com/recipes/640062-312x231.jpg",
        "readyInMinutes": 15,
        "servings": 2,
        "cuisines": ["Mediterranean", "American"],
        "diets": ["gluten free", "dairy free", "keto"],
        "extendedIngredients": [
            {"name": "chicken", "original": "200g Grilled Chicken breast"},
            {"name": "tomato", "original": "1 cup Cherry Tomatoes"},
            {"name": "cucumber", "original": "1 diced Cucumber"},
            {"name": "olive oil", "original": "1 tbsp Olive Oil"},
            {"name": "onion", "original": "1/4 sliced Red Onion"}
        ],
        "nutrition": {
            "nutrients": [
                {"name": "Calories", "amount": 310, "unit": "kcal"},
                {"name": "Protein", "amount": 32, "unit": "g"},
                {"name": "Fat", "amount": 14, "unit": "g"},
                {"name": "Carbohydrates", "amount": 8, "unit": "g"}
            ]
        },
        "analyzedInstructions": [{
            "steps": [
                {"number": 1, "step": "Slice grilled chicken and vegetables."},
                {"number": 2, "step": "Combine in a bowl and drizzle with olive oil and lemon juice."}
            ]
        }]
    },
    {
        "id": 716432,
        "title": "Creamy Garlic Parmesan Chicken",
        "image": "https://img.spoonacular.com/recipes/716432-312x231.jpg",
        "readyInMinutes": 25,
        "servings": 4,
        "cuisines": ["Italian", "European"],
        "diets": ["gluten free", "keto"],
        "extendedIngredients": [
            {"name": "chicken", "original": "4 Chicken breasts"},
            {"name": "garlic", "original": "6 cloves Garlic"},
            {"name": "parmesan cheese", "original": "1/2 cup grated Parmesan"},
            {"name": "heavy cream", "original": "1 cup Heavy Cream"},
            {"name": "spinach", "original": "2 cups Spinach"}
        ],
        "nutrition": {
            "nutrients": [
                {"name": "Calories", "amount": 580, "unit": "kcal"},
                {"name": "Protein", "amount": 46, "unit": "g"},
                {"name": "Fat", "amount": 38, "unit": "g"},
                {"name": "Carbohydrates", "amount": 6, "unit": "g"}
            ]
        },
        "analyzedInstructions": [{
            "steps": [
                {"number": 1, "step": "Sear chicken breasts in pan until golden."},
                {"number": 2, "step": "Add garlic, heavy cream, spinach, and parmesan."},
                {"number": 3, "step": "Simmer for 10 minutes until thick and sauce coats chicken."}
            ]
        }]
    },
    {
        "id": 654959,
        "title": "Paneer Butter Masala",
        "image": "https://img.spoonacular.com/recipes/654959-312x231.jpg",
        "readyInMinutes": 35,
        "servings": 4,
        "cuisines": ["Indian"],
        "diets": ["vegetarian", "gluten free"],
        "extendedIngredients": [
            {"name": "paneer", "original": "300g Paneer cubes"},
            {"name": "tomato", "original": "3 pureed Tomatoes"},
            {"name": "onion", "original": "1 finely chopped Onion"},
            {"name": "garlic", "original": "3 cloves Garlic"},
            {"name": "butter", "original": "2 tbsp Butter"}
        ],
        "nutrition": {
            "nutrients": [
                {"name": "Calories", "amount": 480, "unit": "kcal"},
                {"name": "Protein", "amount": 20, "unit": "g"},
                {"name": "Fat", "amount": 36, "unit": "g"},
                {"name": "Carbohydrates", "amount": 16, "unit": "g"}
            ]
        },
        "analyzedInstructions": [{
            "steps": [
                {"number": 1, "step": "Saute onion and garlic in butter."},
                {"number": 2, "step": "Add tomato puree and Indian spice blend."},
                {"number": 3, "step": "Add paneer cubes and simmer gently for 10 mins."}
            ]
        }]
    }
]

class SpoonacularService:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.SPOONACULAR_API_KEY
        self.base_url = Config.SPOONACULAR_BASE_URL
        self._cache = {}

    def search_candidate_recipes(self, search_params, number=20):
        """
        Retrieves candidate recipes from Spoonacular API based on user search parameters.
        Uses in-memory cache to save API quota.
        Falls back gracefully to mock data if API request fails or key is missing.
        """
        # If API key is missing or dummy placeholder, use mock candidates
        if not self.api_key or self.api_key == 'your_api_key_here':
            logger.info("Using fallback mock dataset (No API Key provided)")
            return self._get_fallback_mock_data(search_params)

        cache_key = f"{search_params.get('ingredients')}_{search_params.get('diet')}_{search_params.get('cuisine')}_{search_params.get('meal_type')}_{number}"
        if cache_key in self._cache:
            cache_time, cached_data = self._cache[cache_key]
            if time.time() - cache_time < Config.CACHE_TIMEOUT:
                logger.info("Returning cached Spoonacular response")
                return cached_data

        params = {
            'apiKey': self.api_key,
            'number': number,
            'addRecipeInformation': True,
            'addRecipeNutrition': True,
            'fillIngredients': True
        }

        if search_params.get('ingredients'):
            params['includeIngredients'] = search_params['ingredients']

        if search_params.get('diet') and search_params['diet'] != 'None':
            params['diet'] = search_params['diet'].lower()

        if search_params.get('cuisine') and search_params['cuisine'] != 'Any':
            params['cuisine'] = search_params['cuisine']

        if search_params.get('meal_type') and search_params['meal_type'] != 'Any':
            params['type'] = search_params['meal_type'].lower()

        if search_params.get('allergies'):
            params['excludeIngredients'] = search_params['allergies']

        if search_params.get('max_cooking_time'):
            params['maxReadyTime'] = search_params['max_cooking_time']

        try:
            url = f"{self.base_url}/complexSearch"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                if results:
                    self._cache[cache_key] = (time.time(), results)
                    return results
                else:
                    # If live search returned 0 results with strict filters, retry without ingredient restriction
                    logger.info("No recipes found with strict parameters. Retrying broader candidate search.")
                    broader_params = {
                        'apiKey': self.api_key,
                        'number': number,
                        'addRecipeInformation': True,
                        'addRecipeNutrition': True,
                        'fillIngredients': True
                    }
                    if search_params.get('diet') and search_params['diet'] != 'None':
                        broader_params['diet'] = search_params['diet'].lower()
                    
                    retry_res = requests.get(url, params=broader_params, timeout=10)
                    if retry_res.status_code == 200:
                        retry_data = retry_res.json()
                        results = retry_data.get('results', [])
                        if results:
                            self._cache[cache_key] = (time.time(), results)
                            return results
                            
                    return self._get_fallback_mock_data(search_params)
            else:
                logger.warning(f"Spoonacular API error ({response.status_code}): {response.text}")
                return self._get_fallback_mock_data(search_params)

        except Exception as e:
            logger.error(f"Spoonacular request exception: {e}")
            return self._get_fallback_mock_data(search_params)

    def get_recipe_details(self, recipe_id):
        """Fetches detailed recipe information by ID."""
        if not self.api_key or self.api_key == 'your_api_key_here':
            for r in MOCK_RECIPES:
                if str(r['id']) == str(recipe_id):
                    return r
            return MOCK_RECIPES[0]

        try:
            url = f"{self.base_url}/{recipe_id}/information"
            params = {
                'apiKey': self.api_key,
                'includeNutrition': True
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                for r in MOCK_RECIPES:
                    if str(r['id']) == str(recipe_id):
                        return r
                return MOCK_RECIPES[0]
        except Exception:
            for r in MOCK_RECIPES:
                if str(r['id']) == str(recipe_id):
                    return r
            return MOCK_RECIPES[0]

    def _get_fallback_mock_data(self, search_params):
        """Returns mock recipe candidates when API is unavailable."""
        return MOCK_RECIPES
