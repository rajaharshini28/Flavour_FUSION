from flask import Blueprint, render_template, current_app
from database.repository import Repository

history_bp = Blueprint('history', __name__)

@history_bp.route('/history')
def history():
    repo = Repository(current_app.config['DATABASE_PATH'])
    searches = repo.get_recent_searches(user_id=1, limit=30)
    interactions = repo.get_user_interactions(user_id=1, limit=30)
    
    return render_template(
        'history.html',
        searches=searches,
        interactions=interactions
    )
