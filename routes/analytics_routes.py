import json
import pandas as pd
from flask import Blueprint, render_template, current_app
from database.repository import Repository

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
def analytics():
    repo = Repository(current_app.config['DATABASE_PATH'])
    
    searches = repo.get_all_searches()
    recommendations = repo.get_all_recommendations()
    interactions = repo.get_all_interactions()
    
    # Initialize metrics defaults
    total_searches = len(searches)
    total_recommendations = len(recommendations)
    total_interactions = len(interactions)
    
    top_ingredients = []
    top_cuisines = []
    top_diets = []
    top_recipes = []
    avg_score = 0.0
    avg_ingredient_score = 0.0
    top_missing_ingredients = []
    
    # Process Searches with Pandas if data exists
    if searches:
        df_searches = pd.DataFrame(searches)
        
        # Most Searched Ingredients
        raw_ings = df_searches['ingredients'].dropna().str.cat(sep=',').split(',')
        clean_ings = [i.strip().lower() for i in raw_ings if i.strip()]
        if clean_ings:
            s_ings = pd.Series(clean_ings).value_counts().head(5)
            top_ingredients = [{'name': k.title(), 'count': int(v)} for k, v in s_ings.items()]
            
        # Most Preferred Cuisines
        if 'cuisine' in df_searches and not df_searches['cuisine'].empty:
            s_cuisines = df_searches[df_searches['cuisine'] != 'Any']['cuisine'].value_counts().head(5)
            top_cuisines = [{'name': k, 'count': int(v)} for k, v in s_cuisines.items()]
            
        # Most Common Dietary Preferences
        if 'diet' in df_searches and not df_searches['diet'].empty:
            s_diets = df_searches[df_searches['diet'] != 'None']['diet'].value_counts().head(5)
            top_diets = [{'name': k, 'count': int(v)} for k, v in s_diets.items()]

    # Process Recommendations with Pandas if data exists
    if recommendations:
        df_recs = pd.DataFrame(recommendations)
        
        if 'recommendation_score' in df_recs:
            avg_score = round(float(df_recs['recommendation_score'].mean()), 1)
        if 'ingredient_score' in df_recs:
            avg_ingredient_score = round(float(df_recs['ingredient_score'].mean()), 1)
            
        # Frequently missing ingredients
        missing_list = []
        for missing_json in df_recs['missing_ingredients'].dropna():
            try:
                items = json.loads(missing_json) if isinstance(missing_json, str) else missing_json
                if isinstance(items, list):
                    missing_list.extend([str(x).strip().lower() for x in items])
            except Exception:
                pass
                
        if missing_list:
            s_missing = pd.Series(missing_list).value_counts().head(5)
            top_missing_ingredients = [{'name': k.title(), 'count': int(v)} for k, v in s_missing.items()]

    # Process Recipe Interactions with Pandas if data exists
    if interactions:
        df_inter = pd.DataFrame(interactions)
        if 'recipe_name' in df_inter and not df_inter['recipe_name'].empty:
            s_recipes = df_inter['recipe_name'].value_counts().head(5)
            top_recipes = [{'name': k, 'count': int(v)} for k, v in s_recipes.items()]

    analytics_data = {
        'total_searches': total_searches,
        'total_recommendations': total_recommendations,
        'total_interactions': total_interactions,
        'avg_score': avg_score,
        'avg_ingredient_score': avg_ingredient_score,
        'top_ingredients': top_ingredients,
        'top_cuisines': top_cuisines,
        'top_diets': top_diets,
        'top_recipes': top_recipes,
        'top_missing_ingredients': top_missing_ingredients
    }
    
    return render_template('analytics.html', analytics=analytics_data)
