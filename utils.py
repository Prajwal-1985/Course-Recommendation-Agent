"""Utility functions for the Course Recommendation Agent."""

import json
import os
from typing import List, Dict, Any

from models import Course, Student


def load_courses(filepath: str = "data/courses.json") -> List[Course]:
    """Load courses from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    courses = []
    for c in data["courses"]:
        courses.append(Course(
            id=c["id"],
            title=c["title"],
            description=c["description"],
            skills_taught=c["skills_taught"],
            prerequisites=c["prerequisites"],
            difficulty=c["difficulty"],
            estimated_hours=c["estimated_hours"],
            category=c["category"]
        ))
    return courses


def load_sample_students(filepath: str = "data/sample_students.json") -> List[Student]:
    """Load sample student profiles from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    students = []
    for s in data["students"]:
        students.append(Student(
            name=s["name"],
            background=s["background"],
            current_skills=s["current_skills"],
            skill_level=s["skill_level"],
            career_goal=s["career_goal"],
            study_hours_per_week=s["study_hours_per_week"]
        ))
    return students


def normalize_skills(skills: List[str]) -> List[str]:
    """Normalize skill names to lowercase with hyphens."""
    normalized = []
    for skill in skills:
        ns = skill.strip().lower().replace(" ", "-").replace("_", "-")
        normalized.append(ns)
    return normalized


def validate_student(student: Student, all_skills: set) -> List[str]:
    """Validate student skills against known skills. Return warnings."""
    warnings = []
    for skill in student.current_skills:
        if skill not in all_skills:
            warnings.append(f"Unknown skill '{skill}' will be ignored.")
    return warnings


def get_all_skills_from_courses(courses: List[Course]) -> set:
    """Extract all known skills from the course catalogue."""
    skills = set()
    for course in courses:
        skills.update(course.skills_taught)
    return skills


def format_hours(hours: int) -> str:
    """Format hours into a readable string."""
    if hours < 24:
        return f"{hours} hours"
    days = hours // 8
    remaining = hours % 8
    if remaining == 0:
        return f"{hours} hours (~{days} full days)"
    return f"{hours} hours (~{days} full days + {remaining} hours)"
