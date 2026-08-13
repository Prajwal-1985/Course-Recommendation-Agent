#!/usr/bin/env python3
"""Course Recommendation Agent — CLI Entry Point."""

import json
import sys
import os
from typing import Optional

from models import Student
from utils import load_courses, load_sample_students, validate_student, get_all_skills_from_courses, format_hours
from recommender import recommend
from llm import enhance_with_llm


def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("   COURSE RECOMMENDATION AGENT")
    print("   ROOMAN AI CHALLENGE — Junior AI Research Associate")
    print("=" * 60)
    print()


def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default value."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def parse_skills_input(skills_str: str) -> list:
    """Parse comma-separated skills into a list."""
    if not skills_str:
        return []
    return [s.strip() for s in skills_str.split(",") if s.strip()]


def interactive_mode(courses):
    """Run the agent in interactive CLI mode."""
    print("\n--- Interactive Mode ---\n")

    name = get_input("Name")
    background = get_input("Background (e.g., 'B.Tech CSE student')")
    skills_str = get_input("Current skills (comma-separated)")
    current_skills = parse_skills_input(skills_str)
    skill_level = get_input("Skill level (beginner/intermediate/advanced)", "beginner")
    career_goal = get_input("Career goal (e.g., 'Data Scientist')")
    study_hours = get_input("Study hours per week", "10")

    try:
        study_hours = int(study_hours)
    except ValueError:
        study_hours = 10

    student = Student(
        name=name,
        background=background,
        current_skills=current_skills,
        skill_level=skill_level.lower(),
        career_goal=career_goal,
        study_hours_per_week=study_hours
    )

    process_student(student, courses)


def process_student(student: Student, courses, output_prefix: Optional[str] = None):
    """Process a single student and print/save results."""
    all_skills = get_all_skills_from_courses(courses)
    warnings = validate_student(student, all_skills)

    if warnings:
        print("\n[Warnings]")
        for w in warnings:
            print(f"  ⚠ {w}")

    print(f"\n📋 Processing recommendation for {student.name}...")

    # Generate recommendation
    result = recommend(student, courses)

    # Enhance with LLM (or fallback)
    enhance_with_llm(result)

    # Display results
    display_result(result)

    # Save to file if prefix provided
    if output_prefix:
        save_result(result, output_prefix)

    return result


def display_result(result):
    """Display the recommendation result in a clean format."""
    s = result.student

    print("\n" + "=" * 60)
    print("STUDENT PROFILE")
    print("=" * 60)
    print(f"  Name:           {s.name}")
    print(f"  Background:     {s.background}")
    print(f"  Skill Level:    {s.skill_level}")
    print(f"  Career Goal:    {s.career_goal}")
    print(f"  Study Time:     {s.study_hours_per_week} hours/week")

    print("\n" + "-" * 60)
    print("IDENTIFIED SKILL GAPS")
    print("-" * 60)
    if result.skill_gaps:
        for gap in result.skill_gaps:
            print(f"  • {gap}")
    else:
        print("  ✓ No skill gaps identified — strong foundation!")

    print("\n" + "-" * 60)
    print("RECOMMENDED LEARNING PATH")
    print("-" * 60)

    for item in result.learning_path:
        print(f"\n  {item.order}. {item.course.title}")
        print(f"     Category:     {item.course.category}")
        print(f"     Difficulty:   {item.course.difficulty}")
        print(f"     Duration:     {item.course.estimated_hours} hours")
        print(f"     Why:          {item.reason}")
        if item.llm_explanation:
            print(f"     💡 {item.llm_explanation}")

    print("\n" + "-" * 60)
    print("SUMMARY")
    print("-" * 60)
    print(f"  Total Courses:      {len(result.learning_path)}")
    print(f"  Total Learning Time: {format_hours(result.total_hours)}")
    print(f"  Estimated Duration:  ~{result.estimated_weeks} weeks")

    if result.overall_explanation:
        print(f"\n  📌 Strategy: {result.overall_explanation}")

    if result.next_milestone:
        print(f"\n  🎯 Next Milestone: {result.next_milestone}")

    print("\n" + "=" * 60)


def save_result(result, prefix: str):
    """Save the result to JSON and text files."""
    os.makedirs("outputs", exist_ok=True)

    # JSON output
    json_data = {
        "student": {
            "name": result.student.name,
            "background": result.student.background,
            "current_skills": result.student.current_skills,
            "skill_level": result.student.skill_level,
            "career_goal": result.student.career_goal,
            "study_hours_per_week": result.student.study_hours_per_week
        },
        "target_skills": result.target_skills,
        "skill_gaps": result.skill_gaps,
        "learning_path": [
            {
                "order": item.order,
                "course_id": item.course.id,
                "title": item.course.title,
                "category": item.course.category,
                "difficulty": item.course.difficulty,
                "estimated_hours": item.course.estimated_hours,
                "deterministic_reason": item.reason,
                "personalized_explanation": item.llm_explanation
            }
            for item in result.learning_path
        ],
        "total_hours": result.total_hours,
        "estimated_weeks": result.estimated_weeks,
        "overall_explanation": result.overall_explanation,
        "next_milestone": result.next_milestone
    }

    json_path = f"outputs/{prefix}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved structured output to {json_path}")

    # Text output
    text_path = f"outputs/{prefix}.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(f"COURSE RECOMMENDATION AGENT\n")
        f.write(f"Generated for: {result.student.name}\n\n")
        f.write(f"STUDENT PROFILE\n")
        f.write(f"  Name: {result.student.name}\n")
        f.write(f"  Background: {result.student.background}\n")
        f.write(f"  Skill Level: {result.student.skill_level}\n")
        f.write(f"  Career Goal: {result.student.career_goal}\n")
        f.write(f"  Study Time: {result.student.study_hours_per_week} hours/week\n\n")

        f.write(f"IDENTIFIED SKILL GAPS\n")
        if result.skill_gaps:
            for gap in result.skill_gaps:
                f.write(f"  • {gap}\n")
        else:
            f.write(f"  ✓ No skill gaps identified\n")
        f.write("\n")

        f.write(f"RECOMMENDED LEARNING PATH\n")
        for item in result.learning_path:
            f.write(f"\n{item.order}. {item.course.title}\n")
            f.write(f"   Category: {item.course.category}\n")
            f.write(f"   Difficulty: {item.course.difficulty}\n")
            f.write(f"   Duration: {item.course.estimated_hours} hours\n")
            f.write(f"   Why: {item.reason}\n")
            if item.llm_explanation:
                f.write(f"   Personalized: {item.llm_explanation}\n")

        f.write(f"\nSUMMARY\n")
        f.write(f"  Total Courses: {len(result.learning_path)}\n")
        f.write(f"  Total Hours: {result.total_hours}\n")
        f.write(f"  Estimated Weeks: {result.estimated_weeks}\n")
        if result.overall_explanation:
            f.write(f"\nStrategy: {result.overall_explanation}\n")
        if result.next_milestone:
            f.write(f"\nNext Milestone: {result.next_milestone}\n")

    print(f"💾 Saved text output to {text_path}")


def demo_mode(courses):
    """Run the agent on all sample students."""
    print("\n--- Demo Mode: Running all sample students ---\n")
    students = load_sample_students("data/sample_students.json")

    for student in students:
        safe_name = student.name.lower().replace(" ", "_")
        process_student(student, courses, output_prefix=f"sample_{safe_name}")
        print("\n")


def main():
    """Main entry point."""
    print_banner()

    # Load course catalogue
    try:
        courses = load_courses("data/courses.json")
        print(f"✅ Loaded {len(courses)} courses from catalogue.")
    except FileNotFoundError:
        print("❌ Error: data/courses.json not found. Make sure you're running from the project root.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading courses: {e}")
        sys.exit(1)

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ("--demo", "-d"):
            demo_mode(courses)
        elif sys.argv[1] in ("--interactive", "-i"):
            interactive_mode(courses)
        elif sys.argv[1] in ("--help", "-h"):
            print_help()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print_help()
    else:
        # Default: run interactive mode
        interactive_mode(courses)


def print_help():
    """Print help message."""
    print("""
Usage: python app.py [OPTION]

Options:
  --interactive, -i    Run in interactive mode (default)
  --demo, -d           Run on all sample student profiles
  --help, -h           Show this help message

Environment Variables:
  LLM_API_KEY          API key for LLM service (optional)
  LLM_BASE_URL         Base URL for LLM API (default: OpenRouter)
  LLM_MODEL            Model name (default: openai/gpt-3.5-turbo)

Without an LLM_API_KEY, the agent uses deterministic explanations.
""")


if __name__ == "__main__":
    main()
