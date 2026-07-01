import json
from dotenv import load_dotenv
load_dotenv()
from src.config import settings
from src.data.cache import get_all_restaurants
from src.filtering.filter import filter_restaurants, prepare_candidates
from src.api.models import UserPreferences
from src.llm.prompt_builder import build_prompt
from src.llm.groq_client import GroqClient
from src.llm.parser import parse_llm_response

def run_prediction():
    print("Loading dataset...")
    restaurants = get_all_restaurants()
    
    # Let's find out which tier 1500 falls into, roughly.
    # In ingestion.py: low is <= 33%, high is > 67%
    # We will just map 1500 to a tier based on the dataset.
    import pandas as pd
    df = pd.DataFrame([r.model_dump() for r in restaurants])
    low_thresh = df["cost_for_two"].quantile(0.33)
    high_thresh = df["cost_for_two"].quantile(0.67)
    
    budget_val = 1300
    if budget_val <= low_thresh:
        budget_tier = "low"
    elif budget_val <= high_thresh:
        budget_tier = "medium"
    else:
        budget_tier = "high"
        
    print(f"Cost {budget_val} mapped to budget tier: {budget_tier} (low<={low_thresh}, high>{high_thresh})")
    
    prefs = UserPreferences(
        location="Banashankari",
        min_rating=4.0,
        budget=budget_tier,
        additional_preferences="Cost for two should be around 1300."
    )
    
    # 2. Filter
    print(f"Filtering for location={prefs.location}, min_rating={prefs.min_rating}, budget={prefs.budget}...")
    filtered = filter_restaurants(
        restaurants, 
        location=prefs.location, 
        min_rating=prefs.min_rating,
        budget=prefs.budget
    )
    
    if not filtered:
        print("No restaurants found matching the exact filters. Relaxing budget filter...")
        filtered = filter_restaurants(
            restaurants, 
            location=prefs.location, 
            min_rating=prefs.min_rating
        )
    
    # 3. Prepare Candidates
    candidates, total = prepare_candidates(filtered, max_candidates=settings.max_candidates)
    print(f"Found {total} filtered restaurants, using top {len(candidates)} as candidates.")
    
    if not candidates:
        print("Still no candidates found. Exiting.")
        return
        
    # 4. Prompt Builder
    system_prompt, user_prompt = build_prompt(prefs, candidates, top_k=settings.top_k)
    
    # 5. Call LLM
    print("Calling Groq LLM...")
    client = GroqClient(api_key=settings.groq_api_key, model=settings.groq_model, temperature=settings.groq_temperature)
    raw_response = client.get_recommendation(system_prompt, user_prompt)
    
    # 6. Parse Response
    valid_ids = {c["id"] for c in candidates}
    parsed = parse_llm_response(raw_response, valid_ids)
    
    print("\n" + "="*50)
    print("RECOMMENDATION SUMMARY:")
    print("="*50)
    print(parsed.summary)
    print("\nTOP 5 RANKINGS:")
    for rank in parsed.rankings:
        # Find restaurant name
        rest_name = next(c["name"] for c in candidates if c["id"] == rank.restaurant_id)
        cost = next(c["cost_for_two"] for c in candidates if c["id"] == rank.restaurant_id)
        rating = next(c["rating"] for c in candidates if c["id"] == rank.restaurant_id)
        print(f"{rank.rank}. {rest_name} (Rating: {rating}, Cost: {cost})")
        print(f"   Explanation: {rank.explanation}\n")

if __name__ == "__main__":
    run_prediction()
