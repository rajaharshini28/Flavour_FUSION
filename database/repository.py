import json
from database.db import get_db_connection

class Repository:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def _get_conn(self):
        return get_db_connection(self.db_path)

    # USER & PREFERENCES
    def get_user_preferences(self, user_id=1):
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def save_user_preferences(self, user_id, prefs):
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_preferences 
                (user_id, diet, cuisine, meal_type, max_calories, min_protein, max_fat, max_carbs, max_cooking_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    diet=excluded.diet,
                    cuisine=excluded.cuisine,
                    meal_type=excluded.meal_type,
                    max_calories=excluded.max_calories,
                    min_protein=excluded.min_protein,
                    max_fat=excluded.max_fat,
                    max_carbs=excluded.max_carbs,
                    max_cooking_time=excluded.max_cooking_time
            """, (
                user_id,
                prefs.get('diet'),
                prefs.get('cuisine'),
                prefs.get('meal_type'),
                prefs.get('max_calories'),
                prefs.get('min_protein'),
                prefs.get('max_fat'),
                prefs.get('max_carbs'),
                prefs.get('max_cooking_time')
            ))
            conn.commit()
        finally:
            conn.close()

    # SEARCHES
    def save_search(self, user_id, search_params):
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO searches 
                (user_id, ingredients, diet, cuisine, meal_type, allergies, max_calories, min_protein, max_fat, max_carbs, max_cooking_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                search_params.get('ingredients', ''),
                search_params.get('diet', ''),
                search_params.get('cuisine', ''),
                search_params.get('meal_type', ''),
                search_params.get('allergies', ''),
                search_params.get('max_calories'),
                search_params.get('min_protein'),
                search_params.get('max_fat'),
                search_params.get('max_carbs'),
                search_params.get('max_cooking_time')
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_recent_searches(self, user_id=1, limit=20):
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM searches 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    # RECOMMENDATIONS
    def save_recommendations(self, search_id, recommendations):
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            for rec in recommendations:
                matched_str = json.dumps(rec.get('matched_ingredients', []))
                missing_str = json.dumps(rec.get('missing_ingredients', []))
                explanation_str = json.dumps(rec.get('explanation', {}))
                
                cursor.execute("""
                    INSERT INTO recommendations
                    (search_id, recipe_id, recipe_name, image_url, recommendation_score, 
                     ingredient_score, diet_score, nutrition_score, cuisine_score, time_score, history_score,
                     matched_ingredients, missing_ingredients, explanation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    search_id,
                    rec['recipe_id'],
                    rec['title'],
                    rec.get('image', ''),
                    rec['final_score'],
                    rec['component_scores']['ingredient_score'],
                    rec['component_scores']['diet_score'],
                    rec['component_scores']['nutrition_score'],
                    rec['component_scores']['cuisine_score'],
                    rec['component_scores']['time_score'],
                    rec['component_scores']['history_score'],
                    matched_str,
                    missing_str,
                    explanation_str
                ))
            conn.commit()
        finally:
            conn.close()

    def get_recommendations_for_search(self, search_id):
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM recommendations 
                WHERE search_id = ? 
                ORDER BY recommendation_score DESC
            """, (search_id,))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item['matched_ingredients'] = json.loads(item['matched_ingredients']) if item['matched_ingredients'] else []
                item['missing_ingredients'] = json.loads(item['missing_ingredients']) if item['missing_ingredients'] else []
                item['explanation'] = json.loads(item['explanation']) if item['explanation'] else {}
                results.append(item)
            return results
        finally:
            conn.close()

    # RECIPE INTERACTIONS
    def log_recipe_interaction(self, user_id, recipe_id, recipe_name, interaction_type='view'):
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO recipe_interactions (user_id, recipe_id, recipe_name, interaction_type)
                VALUES (?, ?, ?, ?)
            """, (user_id, recipe_id, recipe_name, interaction_type))
            conn.commit()
        finally:
            conn.close()

    def get_user_interactions(self, user_id=1, limit=50):
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM recipe_interactions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # DATA FOR ANALYTICS (PANDAS PROCESSING)
    def get_all_searches(self):
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM searches ORDER BY created_at DESC")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_all_recommendations(self):
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recommendations ORDER BY created_at DESC")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_all_interactions(self):
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipe_interactions ORDER BY created_at DESC")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()
