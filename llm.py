"""LLM integration for personalized explanations with deterministic fallback."""

import os
import json
from typing import Optional

from models import RecommendationResult, PathItem


def get_llm_config() -> dict:
    """Read LLM configuration from environment variables."""
    return {
        "api_key": os.getenv("LLM_API_KEY", ""),
        "base_url": os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
        "model": os.getenv("LLM_MODEL", "openai/gpt-3.5-turbo"),
        "enabled": bool(os.getenv("LLM_API_KEY", ""))
    }


def build_prompt(result: RecommendationResult) -> str:
    """Build a structured prompt for the LLM."""
    student = result.student

    path_text = "\n".join([
        f"{item.order}. {item.course.title} (Difficulty: {item.course.difficulty}, Hours: {item.course.estimated_hours})\n"
        f"   Deterministic reason: {item.reason}"
        for item in result.learning_path
    ])

    prompt = f"""You are an expert course advisor helping a student plan their learning journey.

STUDENT PROFILE:
- Name: {student.name}
- Background: {student.background}
- Current skill level: {student.skill_level}
- Career goal: {student.career_goal}
- Available study time: {student.study_hours_per_week} hours per week

IDENTIFIED SKILL GAPS:
{chr(10).join(f"- {gap}" for gap in result.skill_gaps) if result.skill_gaps else "None — student already has foundational skills."}

RECOMMENDED LEARNING PATH:
{path_text}

TOTAL ESTIMATED TIME: {result.total_hours} hours (~{result.estimated_weeks} weeks at {student.study_hours_per_week} hrs/week)

TASK:
Provide a personalized learning plan. For EACH course in the path, write 2-3 sentences explaining why THIS specific student benefits from it right now, referencing their background and goal. Be encouraging and specific.

Also provide:
1. A brief overall summary (2-3 sentences) of the learning strategy
2. The most important next milestone after completing the path
3. Any additional advice specific to this student

Return your response in this exact JSON format:
{{
  "course_explanations": {{
    "1": "explanation for course 1...",
    "2": "explanation for course 2...",
    ...
  }},
  "overall_summary": "...",
  "next_milestone": "...",
  "additional_advice": "..."
}}

Respond with ONLY the JSON object, no markdown formatting."""

    return prompt


def call_llm(prompt: str, config: dict) -> Optional[dict]:
    """Call the LLM API. Returns parsed JSON or None on failure."""
    if not config["enabled"]:
        return None

    try:
        import requests

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        # Add OpenRouter-specific headers if using OpenRouter
        if "openrouter" in config["base_url"]:
            headers["HTTP-Referer"] = "https://github.com/course-recommendation-agent"
            headers["X-Title"] = "Course Recommendation Agent"

        payload = {
            "model": config["model"],
            "messages": [
                {"role": "system", "content": "You are a helpful course advisor. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        response = requests.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Clean up potential markdown formatting
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        return json.loads(content)

    except Exception as e:
        # Graceful fallback — do not crash
        print(f"[LLM Warning] Could not generate LLM explanations: {e}")
        return None


def generate_fallback_explanations(result: RecommendationResult) -> None:
    """Generate template-based explanations when LLM is unavailable."""
    student = result.student

    for item in result.learning_path:
        course = item.course
        # Create a personalized template explanation
        explanation = (
            f"As a {student.skill_level}-level learner aiming to become a {student.career_goal}, "
            f"'{course.title}' is essential because it {item.reason.lower()}. "
            f"This {course.difficulty} course ({course.estimated_hours} hours) directly supports your goal."
        )
        item.llm_explanation = explanation

    result.overall_explanation = (
        f"Based on your background as {student.background} and your goal to become a {student.career_goal}, "
        f"this learning path covers {len(result.skill_gaps)} skill gaps over approximately {result.estimated_weeks} weeks. "
        f"Start with the foundational courses and progress sequentially."
    )

    if result.learning_path:
        last_course = result.learning_path[-1].course.title
        result.next_milestone = f"After completing '{last_course}', you will be ready to apply for junior {student.career_goal} roles."


def enhance_with_llm(result: RecommendationResult) -> None:
    """
    Enhance recommendation with LLM-generated explanations.
    Falls back to deterministic templates if LLM is unavailable.
    """
    config = get_llm_config()

    if not config["enabled"]:
        print("[Info] No LLM API key found. Using deterministic explanations.")
        generate_fallback_explanations(result)
        return

    prompt = build_prompt(result)
    llm_response = call_llm(prompt, config)

    if llm_response is None:
        generate_fallback_explanations(result)
        return

    # Apply LLM explanations to path items
    course_explanations = llm_response.get("course_explanations", {})
    for item in result.learning_path:
        key = str(item.order)
        if key in course_explanations:
            item.llm_explanation = course_explanations[key]
        else:
            # Fallback for this specific course
            item.llm_explanation = (
                f"'{item.course.title}' builds critical skills for your {result.student.career_goal} journey. "
                f"{item.reason}"
            )

    result.overall_explanation = llm_response.get(
        "overall_summary",
        f"Personalized learning path for {result.student.name} to become a {result.student.career_goal}."
    )
    result.next_milestone = llm_response.get(
        "next_milestone",
        result.next_milestone
    )
