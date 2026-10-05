import re

def normalize_ingredient(ingredient_name: str) -> str:
    """
    Cleans, lowercases, strips whitespace, removes punctuation,
    and performs basic singularization on an ingredient string.
    """
    if not ingredient_name or not isinstance(ingredient_name, str):
        return ""
    
    clean = ingredient_name.lower().strip()
    clean = re.sub(r'[^a-z0-9\s-]', '', clean)
    clean = re.sub(r'\s+', ' ', clean)
    
    # Simple singularization rules for matching
    if clean.endswith('ies') and len(clean) > 4:
        clean = clean[:-3] + 'y'
    elif clean.endswith('es') and len(clean) > 4 and not clean.endswith(('ches', 'shes', 'oxes', 'axes')):
        clean = clean[:-2]
    elif clean.endswith('s') and len(clean) > 3 and not clean.endswith(('ss', 'us', 'is', 'citrus')):
        clean = clean[:-1]
        
    return clean

def parse_ingredient_list(raw_input: str) -> list[str]:
    """
    Parses comma-separated or newline-separated input string into a list of normalized unique ingredients.
    """
    if not raw_input:
        return []
    
    # Split by comma or newline
    tokens = re.split(r'[,;\n]+', str(raw_input))
    processed = []
    seen = set()
    
    for token in tokens:
        normalized = normalize_ingredient(token)
        if normalized and normalized not in seen:
            seen.add(normalized)
            processed.append(normalized)
            
    return processed

def normalize_string_field(value: str) -> str:
    """Normalizes simple text fields (cuisine, diet, meal type)."""
    if not value or not isinstance(value, str):
        return ""
    return value.strip().title()
