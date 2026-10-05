from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from database.repository import Repository
from utils.validators import parse_int_safe

preferences_bp = Blueprint('preferences', __name__)

@preferences_bp.route('/preferences', methods=['GET', 'POST'])
def preferences():
    repo = Repository(current_app.config['DATABASE_PATH'])
    
    if request.method == 'POST':
        prefs = {
            'diet': request.form.get('diet', 'None'),
            'cuisine': request.form.get('cuisine', 'Any'),
            'meal_type': request.form.get('meal_type', 'Any'),
            'max_calories': parse_int_safe(request.form.get('max_calories')),
            'min_protein': parse_int_safe(request.form.get('min_protein')),
            'max_fat': parse_int_safe(request.form.get('max_fat')),
            'max_carbs': parse_int_safe(request.form.get('max_carbs')),
            'max_cooking_time': parse_int_safe(request.form.get('max_cooking_time'))
        }
        repo.save_user_preferences(user_id=1, prefs=prefs)
        flash('Default preferences updated successfully!', 'success')
        return redirect(url_for('preferences.preferences'))
        
    user_prefs = repo.get_user_preferences(user_id=1) or {}
    return render_template('preferences.html', user_prefs=user_prefs)
