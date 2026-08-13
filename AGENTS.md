# Agent Documentation

## Agent Name
Course Recommendation Agent (Beginner)

## Challenge
ROOMAN TECHNOLOGIES — Junior AI Research Associate — 24-Hour AI Agent Challenge

## Capabilities
- Accepts student background, skills, level, goal, and study time
- Maintains a local catalogue of 18 courses with prerequisites
- Calculates skill gaps deterministically
- Recommends an ordered, prerequisite-aware learning path
- Explains every recommendation with deterministic reasoning
- Enhances explanations with optional LLM personalization
- Falls back to deterministic explanations if LLM is unavailable

## Core Files
- `app.py` — CLI entry point
- `recommender.py` — Deterministic recommendation engine
- `llm.py` — LLM client and fallback generator
- `models.py` — Data models
- `utils.py` — Data loading and validation

## Data Files
- `data/courses.json` — Course catalogue
- `data/sample_students.json` — Sample profiles

## Running the Agent
```bash
python app.py --demo
```

## Testing
```bash
python -m pytest tests/test_recommender.py -v
```
