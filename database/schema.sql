-- Flavour Fusion Database Schema (SQLite)

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    diet TEXT,
    cuisine TEXT,
    meal_type TEXT,
    max_calories INTEGER,
    min_protein INTEGER,
    max_fat INTEGER,
    max_carbs INTEGER,
    max_cooking_time INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ingredients TEXT,
    diet TEXT,
    cuisine TEXT,
    meal_type TEXT,
    allergies TEXT,
    max_calories INTEGER,
    min_protein INTEGER,
    max_fat INTEGER,
    max_carbs INTEGER,
    max_cooking_time INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    recipe_name TEXT NOT NULL,
    image_url TEXT,
    recommendation_score REAL NOT NULL,
    ingredient_score REAL NOT NULL,
    diet_score REAL NOT NULL,
    nutrition_score REAL NOT NULL,
    cuisine_score REAL NOT NULL,
    time_score REAL NOT NULL,
    history_score REAL NOT NULL,
    matched_ingredients TEXT,
    missing_ingredients TEXT,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (search_id) REFERENCES searches(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recipe_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    recipe_name TEXT,
    interaction_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
