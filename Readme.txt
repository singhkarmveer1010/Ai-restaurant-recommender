# AI-Powered Restaurant Recommendation System

## Overview
This project is an AI-powered restaurant recommendation service inspired by Zomato. It intelligently suggests restaurants based on user preferences (location, budget, cuisine, ratings) by combining structured restaurant data from a real-world dataset with reasoning from a Large Language Model (Groq).

## Architecture & Workflow
1. Data Ingestion: Loads and preprocesses the Zomato dataset.
2. Filter & Prepare: Deterministically filters restaurants based on hard constraints to reduce the candidate pool.
3. LLM Integration: Passes candidates and user preferences into a prompt.
4. Recommendation Engine: Groq LLM ranks options and generates personalized, human-like explanations.
5. Presentation: A Streamlit UI displays the top recommended restaurants with their ratings, cost, and AI explanation.

## Implementation Phases
- Phase 1: Project Setup & Data Ingestion (Scaffold, dataset load, preprocessing, caching)
- Phase 2: Filter & Prepare Module (Deterministic filtering and candidate serialization)
- Phase 3: Groq LLM Integration (Prompt builder, Groq API client, response parser)
- Phase 4: Recommendation Orchestration (Connecting filter -> LLM -> formatting)
- Phase 5: Streamlit UI & E2E Demo (Web interface for preferences and results)
- Phase 6: Error Handling, Testing & Polish (Fallbacks, edge cases, logging)

## Dataset
- Source: Hugging Face (ManikaSaini/zomato-restaurant-recommendation)
- A local copy of the dataset is available in the `data/restaurent.parquest` file.

## Setup Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment: Copy `.env.example` to `.env` and add your GROQ_API_KEY.
3. Run the application: `streamlit run src/main.py`
