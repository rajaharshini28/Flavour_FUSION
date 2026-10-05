import os
from flask import Flask
from config import Config
from database.db import init_db, get_or_create_default_user

# Route Imports
from routes.main_routes import main_bp
from routes.recommendation_routes import recommendation_bp
from routes.recipe_routes import recipe_bp
from routes.history_routes import history_bp
from routes.preferences_routes import preferences_bp
from routes.analytics_routes import analytics_bp

# Helper Imports for Jinja context
from utils.helpers import format_score, get_score_badge_class

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Database Schema & Default User
    init_db(app.config['DATABASE_PATH'])
    get_or_create_default_user(app.config['DATABASE_PATH'])
    
    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(preferences_bp)
    app.register_blueprint(analytics_bp)
    
    # Register Custom Template Helpers
    app.jinja_env.globals.update(
        format_score=format_score,
        get_score_badge_class=get_score_badge_class
    )
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
