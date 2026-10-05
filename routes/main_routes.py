from flask import Blueprint, render_template, current_app
from database.repository import Repository

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    repo = Repository(current_app.config['DATABASE_PATH'])
    user_prefs = repo.get_user_preferences(user_id=1) or {}
    return render_template('index.html', user_prefs=user_prefs)
