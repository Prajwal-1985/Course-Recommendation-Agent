"""Data models for the Course Recommendation Agent."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Course:
    """Represents a course in the catalogue."""
    id: str
    title: str
    description: str
    skills_taught: List[str]
    prerequisites: List[str]
    difficulty: str  # beginner, intermediate, advanced
    estimated_hours: int
    category: str


@dataclass
class Student:
    """Represents a student profile."""
    name: str
    background: str
    current_skills: List[str]
    skill_level: str  # beginner, intermediate, advanced
    career_goal: str
    study_hours_per_week: int


@dataclass
class PathItem:
    """A single item in the recommended learning path."""
    order: int
    course: Course
    reason: str  # deterministic reason
    llm_explanation: Optional[str] = None


@dataclass
class RecommendationResult:
    """The complete recommendation output."""
    student: Student
    target_skills: List[str]
    skill_gaps: List[str]
    learning_path: List[PathItem]
    total_hours: int
    estimated_weeks: float
    overall_explanation: Optional[str] = None
    next_milestone: Optional[str] = None
