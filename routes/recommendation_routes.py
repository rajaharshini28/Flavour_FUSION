from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from database.repository import Repository
from services.spoonacular_service import SpoonacularService
from services.recommendation_engine import RecommendationEngine
from utils.validators import validate_search_inputs

recommendation_bp = Blueprint('recommendation', __name__)

@recommendation_bp.route('/recommend', methods=['POST', 'GET'])
def recommend():
    repo = Repository(current_app.config['DATABASE_PATH'])
    
    if request.method == 'POST':
        search_params, errors = validate_search_inputs(request.form)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return redirect(url_for('main.index'))
            
        # 1. Save Search in SQLite DB
        search_id = repo.save_search(user_id=1, search_params=search_params)
        
        # 2. Retrieve Candidate Recipes from Spoonacular API
        spoonacular = SpoonacularService(api_key=current_app.config['SPOONACULAR_API_KEY'])
        raw_candidates = spoonacular.search_candidate_recipes(search_params, number=20)
        
        # 3. Run Recommendation Pipeline (Scoring, Filtering, Personalization, Ranking)
        engine = RecommendationEngine()
        ranked_recipes = engine.process_and_rank_recipes(raw_candidates, search_params, user_id=1)
        
        # 4. Save Recommendations to SQLite
        if ranked_recipes:
            repo.save_recommendations(search_id=search_id, recommendations=ranked_recipes)
            
        return render_template(
            'recommendations.html',
            recipes=ranked_recipes,
            search_params=search_params,
            search_id=search_id,
            total_found=len(ranked_recipes)
        )
    else:
        # GET request with search_id parameter
        search_id = request.args.get('search_id')
        if search_id:
            recs = repo.get_recommendations_for_search(search_id)
            return render_template(
                'recommendations.html',
                recipes=recs,
                search_params={},
                search_id=search_id,
                total_found=len(recs)
            )
        return redirect(url_for('main.index'))
