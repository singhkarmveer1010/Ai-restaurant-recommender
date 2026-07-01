# Project Context: AI-Powered Restaurant Recommendation System

## Overview

This project is an **AI-powered restaurant recommendation service** inspired by **Zomato**. The system intelligently suggests restaurants based on user preferences by combining **structured restaurant data** with a **Large Language Model (LLM)**.

## Objective

Design and implement an application that:

- Takes user preferences (such as location, budget, cuisine, and ratings)
- Uses a real-world dataset of restaurants
- Leverages an LLM to generate personalized, human-like recommendations
- Displays clear and useful results to the user

## Data Source

- **Dataset:** Zomato restaurant recommendation dataset on Hugging Face
- **URL:** https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation
- **Relevant fields:** restaurant name, location, cuisine, cost, rating, and related metadata

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face
- Extract relevant fields such as restaurant name, location, cuisine, cost, rating, etc.

### 2. User Input

Collect user preferences:

| Preference | Examples |
|------------|----------|
| Location | Delhi, Bangalore |
| Budget | low, medium, high |
| Cuisine | Italian, Chinese |
| Minimum rating | numeric threshold |
| Additional preferences | family-friendly, quick service |

### 3. Integration Layer

- Filter and prepare relevant restaurant data based on user input
- Pass structured results into an LLM prompt
- Design a prompt that helps the LLM reason and rank options

### 4. Recommendation Engine

Use the LLM to:

- Rank restaurants
- Provide explanations (why each recommendation fits)
- Optionally summarize choices

### 5. Output Display

Present top recommendations in a user-friendly format:

- Restaurant Name
- Cuisine
- Rating
- Estimated Cost
- AI-generated explanation

## Key Requirements Summary

1. **Structured filtering** — Narrow the dataset using explicit user criteria before LLM processing.
2. **LLM reasoning** — Use the model to rank, explain, and optionally summarize recommendations.
3. **Human-like output** — Recommendations should feel personalized and conversational, not just raw data rows.
4. **Clear UX** — Results must be easy to read and actionable for the end user.

## Technical Considerations

- **Data pipeline:** Hugging Face dataset load → preprocess → field extraction
- **User interface:** Form or input mechanism for preference collection
- **Integration:** Bridge between filtered structured data and LLM prompt
- **Prompt design:** Critical for ranking quality and explanation clarity
- **Output formatting:** Consistent presentation of name, cuisine, rating, cost, and explanation

## Success Criteria

The application successfully:

- Accepts and validates user preferences
- Filters the Zomato dataset appropriately
- Produces ranked, explained recommendations via LLM
- Displays results in a clear, user-friendly format
