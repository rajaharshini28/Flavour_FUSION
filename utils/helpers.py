def format_score(score: float) -> str:
    """Formats numeric recommendation score into clean percentage string."""
    try:
        return f"{round(float(score), 1)}%"
    except (ValueError, TypeError):
        return "0.0%"

def get_score_badge_class(score: float) -> str:
    """Returns CSS class based on recommendation score tier."""
    if score >= 85:
        return "badge-excellent"
    elif score >= 70:
        return "badge-good"
    elif score >= 50:
        return "badge-fair"
    else:
        return "badge-low"
