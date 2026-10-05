import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-flavour-fusion-secret-key')
    SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY', '')
    SPOONACULAR_BASE_URL = 'https://api.spoonacular.com/recipes'
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'flavour_fusion.db')
    
    # Recommendation Engine Weights (Total = 1.0)
    INGREDIENT_WEIGHT = 0.40
    DIET_WEIGHT = 0.20
    NUTRITION_WEIGHT = 0.15
    CUISINE_WEIGHT = 0.10
    TIME_WEIGHT = 0.10
    HISTORY_WEIGHT = 0.05

    # Cache expiration in seconds (1 hour)
    CACHE_TIMEOUT = 3600
