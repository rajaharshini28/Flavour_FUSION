from utils.validators import parse_int_safe, validate_search_inputs

def test_parse_int_safe():
    assert parse_int_safe("50") == 50
    assert parse_int_safe("", default=None) is None
    assert parse_int_safe("invalid", default=10) == 10
    assert parse_int_safe("-100", min_val=0) == 0
    assert parse_int_safe("99999", max_val=1000) == 1000

def test_validate_search_inputs():
    form_data = {
        'ingredients': 'chicken, tomato',
        'diet': 'Gluten Free',
        'cuisine': 'Indian',
        'max_calories': '600',
        'min_protein': '25'
    }
    
    sanitized, errors = validate_search_inputs(form_data)
    
    assert errors == []
    assert sanitized['ingredients'] == 'chicken, tomato'
    assert sanitized['diet'] == 'Gluten Free'
    assert sanitized['max_calories'] == 600
    assert sanitized['min_protein'] == 25
