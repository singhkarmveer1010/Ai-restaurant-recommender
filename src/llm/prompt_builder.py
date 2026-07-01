"""
Prompt construction for the Groq LLM.
"""

import json
from src.api.models import UserPreferences

SYSTEM_PROMPT_TEMPLATE = """\
You are an expert restaurant recommender. You MUST ONLY recommend
restaurants from the provided candidate list. Do NOT invent or 
hallucinate any restaurant not in the list.

Given the user's preferences and the candidate restaurants below,
rank the top {top_k} restaurants. For each, provide a concise 
1-2 sentence explanation of why it's a good match.

Respond ONLY in valid JSON with this exact structure:
{{
  "summary": "A brief 1-2 sentence overview",
  "rankings": [
    {{
      "restaurant_id": "string",
      "rank": 1,
      "explanation": "string"
    }}
  ]
}}
"""

USER_PROMPT_TEMPLATE = """\
## My Preferences
- Location: {location}
- Budget: {budget}
- Cuisine: {cuisine}
- Minimum Rating: {min_rating}
- Additional: {additional_preferences}

## Candidate Restaurants
{candidates_json}

Please rank the top {top_k} from the list above.
"""

def build_prompt(
    preferences: UserPreferences,
    candidates: list[dict],
    top_k: int
) -> tuple[str, str]:
    """
    Constructs the system and user prompts for the LLM.

    Returns
    -------
    tuple[str, str]
        (system_prompt, user_prompt)
    """
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(top_k=top_k)
    
    candidates_json = json.dumps(candidates, indent=2)
    
    user_prompt = USER_PROMPT_TEMPLATE.format(
        location=preferences.location or "Any",
        budget=preferences.budget or "Any",
        cuisine=preferences.cuisine or "Any",
        min_rating=preferences.min_rating if preferences.min_rating > 0 else "Any",
        additional_preferences=preferences.additional_preferences or "None",
        candidates_json=candidates_json,
        top_k=top_k
    )
    
    return system_prompt, user_prompt
