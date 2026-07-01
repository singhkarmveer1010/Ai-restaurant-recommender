"""
Unit tests for LLM response parser.
"""

import pytest
from src.llm.parser import parse_llm_response, ParseError

def test_valid_json():
    raw_json = '''
    {
      "summary": "Great options",
      "rankings": [
        {"restaurant_id": "r1", "rank": 1, "explanation": "Good food"},
        {"restaurant_id": "r2", "rank": 2, "explanation": "Nice vibe"}
      ]
    }
    '''
    valid_ids = {"r1", "r2", "r3"}
    res = parse_llm_response(raw_json, valid_ids)
    
    assert res.summary == "Great options"
    assert len(res.rankings) == 2
    assert res.rankings[0].restaurant_id == "r1"
    assert res.rankings[0].rank == 1

def test_unknown_id_stripped():
    raw_json = '''
    {
      "summary": "Overview",
      "rankings": [
        {"restaurant_id": "r1", "rank": 1, "explanation": "Good food"},
        {"restaurant_id": "r_unknown", "rank": 2, "explanation": "Hallucinated"},
        {"restaurant_id": "r2", "rank": 3, "explanation": "Nice vibe"}
      ]
    }
    '''
    valid_ids = {"r1", "r2"}
    res = parse_llm_response(raw_json, valid_ids)
    
    assert len(res.rankings) == 2
    # Ranks should be re-numbered
    assert res.rankings[0].restaurant_id == "r1"
    assert res.rankings[0].rank == 1
    assert res.rankings[1].restaurant_id == "r2"
    assert res.rankings[1].rank == 2

def test_malformed_json():
    raw_json = '{ invalid json'
    with pytest.raises(ParseError):
        parse_llm_response(raw_json, {"r1"})

def test_empty_rankings():
    raw_json = '{"summary": "Test", "rankings": []}'
    with pytest.raises(ParseError, match="non-empty list"):
        parse_llm_response(raw_json, {"r1"})

def test_all_unknown_ids():
    raw_json = '{"summary": "Test", "rankings": [{"restaurant_id": "x", "rank": 1}]}'
    with pytest.raises(ParseError, match="No valid restaurant IDs found"):
        parse_llm_response(raw_json, {"r1"})
