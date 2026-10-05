from flask import Blueprint, render_template, current_app
from database.repository import Repository
from services.spoonacular_service import SpoonacularService

recipe_bp = Blueprint('recipe', __name__)

@recipe_bp.route('/recipe/<int:recipe_id>')
def recipe_details(recipe_id):
    repo = Repository(current_app.config['DATABASE_PATH'])
    spoonacular = SpoonacularService(api_key=current_app.config['SPOONACULAR_API_KEY'])
    
    recipe_data = spoonacular.get_recipe_details(recipe_id)
    recipe_name = recipe_data.get('title', f"Recipe #{recipe_id}")
    
    # Log interaction for user profile personalization
    repo.log_recipe_interaction(user_id=1, recipe_id=recipe_id, recipe_name=recipe_name, interaction_type='view')
    
    return render_template('recipe_details.html', recipe=recipe_data)
