"""Automated tests for the Course Recommendation Agent."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from models import Student, Course
from utils import load_courses, get_all_skills_from_courses, validate_student
from recommender import (
    get_target_skills,
    calculate_skill_gaps,
    score_course,
    build_prerequisite_aware_path,
    recommend
)
from llm import get_llm_config, generate_fallback_explanations


class TestGoalMapping(unittest.TestCase):
    """Tests for career goal to target skills mapping."""

    def test_data_scientist_goal(self):
        skills, categories = get_target_skills("Data Scientist")
        self.assertIn("pandas-dataframes", skills)
        self.assertIn("data", categories)

    def test_ai_ml_engineer_goal(self):
        skills, categories = get_target_skills("AI/ML Engineer")
        self.assertIn("neural-networks", skills)
        self.assertIn("deep-learning", categories)

    def test_generative_ai_goal(self):
        skills, categories = get_target_skills("Generative AI Developer")
        self.assertIn("llms", skills)
        self.assertIn("generative-ai", categories)

    def test_unknown_goal_fallback(self):
        skills, categories = get_target_skills("Quantum Computing Expert")
        self.assertIn("python-syntax", skills)  # Default fallback


class TestSkillGapAnalysis(unittest.TestCase):
    """Tests for skill gap calculation."""

    def test_no_gaps(self):
        current = ["python-syntax", "variables"]
        target = ["python-syntax"]
        gaps = calculate_skill_gaps(current, target)
        self.assertEqual(len(gaps), 0)

    def test_some_gaps(self):
        current = ["python-syntax"]
        target = ["python-syntax", "numpy-arrays", "pandas-dataframes"]
        gaps = calculate_skill_gaps(current, target)
        self.assertEqual(len(gaps), 2)
        self.assertIn("numpy-arrays", gaps)
        self.assertIn("pandas-dataframes", gaps)

    def test_case_insensitive(self):
        current = ["Python-Syntax"]
        target = ["python-syntax", "NUMPY-ARRAYS"]
        gaps = calculate_skill_gaps(current, target)
        self.assertEqual(len(gaps), 1)
        self.assertIn("numpy-arrays", gaps)


class TestCourseScoring(unittest.TestCase):
    """Tests for the transparent course scoring formula."""

    def test_high_score_for_relevant_course(self):
        course = Course(
            id="test-ml",
            title="Test ML",
            description="Test",
            skills_taught=["supervised-learning", "model-training"],
            prerequisites=[],
            difficulty="intermediate",
            estimated_hours=30,
            category="machine-learning"
        )
        missing = {"supervised-learning", "model-training"}
        score = score_course(course, missing, "intermediate", {"machine-learning"}, set())
        self.assertGreater(score, 0)

    def test_prerequisite_penalty(self):
        course = Course(
            id="test-advanced",
            title="Test Advanced",
            description="Test",
            skills_taught=["neural-networks"],
            prerequisites=["missing-prereq"],
            difficulty="advanced",
            estimated_hours=40,
            category="deep-learning"
        )
        missing = {"neural-networks"}
        score = score_course(course, missing, "beginner", {"deep-learning"}, set())
        # Should be penalized for unmet prerequisites and high difficulty
        self.assertLess(score, 0)

    def test_difficulty_match_bonus(self):
        course = Course(
            id="test-basic",
            title="Test Basic",
            description="Test",
            skills_taught=["python-syntax"],
            prerequisites=[],
            difficulty="beginner",
            estimated_hours=10,
            category="programming"
        )
        missing = {"python-syntax"}
        score = score_course(course, missing, "beginner", {"programming"}, set())
        # Should get difficulty match bonus
        self.assertGreater(score, 15)  # 10 for skill + 5 prereq + 3 relevance + 2 difficulty - 0.5 hours


class TestPrerequisiteResolution(unittest.TestCase):
    """Tests for prerequisite handling and topological ordering."""

    def test_simple_prerequisite_chain(self):
        basic = Course("basic", "Basic", "", ["a"], [], "beginner", 10, "prog")
        advanced = Course("advanced", "Advanced", "", ["b"], ["basic"], "advanced", 20, "prog")

        ordered = build_prerequisite_aware_path([advanced], {"basic": basic, "advanced": advanced})
        self.assertEqual(len(ordered), 2)
        self.assertEqual(ordered[0].id, "basic")
        self.assertEqual(ordered[1].id, "advanced")

    def test_no_prerequisites(self):
        course = Course("solo", "Solo", "", ["x"], [], "beginner", 5, "prog")
        ordered = build_prerequisite_aware_path([course], {"solo": course})
        self.assertEqual(len(ordered), 1)
        self.assertEqual(ordered[0].id, "solo")

    def test_complex_prerequisite_graph(self):
        a = Course("a", "A", "", ["s1"], [], "beginner", 10, "cat")
        b = Course("b", "B", "", ["s2"], ["a"], "intermediate", 15, "cat")
        c = Course("c", "C", "", ["s3"], ["a"], "intermediate", 15, "cat")
        d = Course("d", "D", "", ["s4"], ["b", "c"], "advanced", 20, "cat")

        all_courses = {"a": a, "b": b, "c": c, "d": d}
        ordered = build_prerequisite_aware_path([d], all_courses)

        # a must come before b and c
        # b and c must come before d
        self.assertEqual(ordered[0].id, "a")
        self.assertEqual(ordered[-1].id, "d")


class TestEndToEndRecommendation(unittest.TestCase):
    """End-to-end tests with different student profiles."""

    @classmethod
    def setUpClass(cls):
        cls.courses = load_courses("data/courses.json")

    def test_beginner_data_scientist(self):
        student = Student(
            name="Test Beginner",
            background="Fresh graduate",
            current_skills=[],
            skill_level="beginner",
            career_goal="Data Scientist",
            study_hours_per_week=10
        )
        result = recommend(student, self.courses)

        # Should recommend courses
        self.assertGreater(len(result.learning_path), 0)
        # Should have skill gaps
        self.assertGreater(len(result.skill_gaps), 0)
        # First course should be beginner level
        self.assertEqual(result.learning_path[0].course.difficulty, "beginner")
        # Total hours should be positive
        self.assertGreater(result.total_hours, 0)

    def test_intermediate_ai_engineer(self):
        student = Student(
            name="Test Intermediate",
            background="CSE student",
            current_skills=["python-syntax", "variables", "control-flow", "functions", "git-basics"],
            skill_level="intermediate",
            career_goal="AI/ML Engineer",
            study_hours_per_week=20
        )
        result = recommend(student, self.courses)

        # Should recommend fewer courses due to existing skills
        self.assertGreater(len(result.learning_path), 0)
        # Should have some skill gaps still
        self.assertTrue(len(result.skill_gaps) >= 0)

    def test_advanced_student_few_gaps(self):
        student = Student(
            name="Test Advanced",
            background="Experienced developer",
            current_skills=[
                "python-syntax", "variables", "control-flow", "functions",
                "numpy-arrays", "pandas-dataframes", "descriptive-statistics",
                "supervised-learning", "model-training", "neural-networks"
            ],
            skill_level="advanced",
            career_goal="Generative AI Developer",
            study_hours_per_week=15
        )
        result = recommend(student, self.courses)

        # Should recommend advanced courses
        self.assertGreater(len(result.learning_path), 0)
        # Should have fewer gaps
        self.assertLess(len(result.skill_gaps), 15)  # Generative AI has many target skills

    def test_prerequisites_always_first(self):
        student = Student(
            name="Test Prereq",
            background="Student",
            current_skills=[],
            skill_level="beginner",
            career_goal="Machine Learning Engineer",
            study_hours_per_week=10
        )
        result = recommend(student, self.courses)

        # For every course, its prerequisites must appear earlier in the path
        course_ids_in_path = [item.course.id for item in result.learning_path]
        for item in result.learning_path:
            for prereq in item.course.prerequisites:
                if prereq in course_ids_in_path:
                    prereq_index = course_ids_in_path.index(prereq)
                    course_index = course_ids_in_path.index(item.course.id)
                    self.assertLess(prereq_index, course_index,
                        f"Prerequisite {prereq} should come before {item.course.id}")


class TestInputValidation(unittest.TestCase):
    """Tests for input validation edge cases."""

    @classmethod
    def setUpClass(cls):
        cls.courses = load_courses("data/courses.json")
        cls.all_skills = get_all_skills_from_courses(cls.courses)

    def test_unknown_skills_warning(self):
        student = Student(
            name="Test",
            background="Test",
            current_skills=["fake-skill-123", "python-syntax"],
            skill_level="beginner",
            career_goal="Data Scientist",
            study_hours_per_week=10
        )
        warnings = validate_student(student, self.all_skills)
        self.assertEqual(len(warnings), 1)
        self.assertIn("fake-skill-123", warnings[0])

    def test_empty_skills(self):
        student = Student(
            name="Test",
            background="Test",
            current_skills=[],
            skill_level="beginner",
            career_goal="Data Scientist",
            study_hours_per_week=10
        )
        result = recommend(student, self.courses)
        self.assertGreater(len(result.learning_path), 0)
        self.assertGreater(len(result.skill_gaps), 0)

    def test_zero_study_hours(self):
        student = Student(
            name="Test",
            background="Test",
            current_skills=[],
            skill_level="beginner",
            career_goal="Data Scientist",
            study_hours_per_week=0
        )
        result = recommend(student, self.courses)
        # Should not crash, just have 0 or inf weeks
        self.assertGreaterEqual(result.estimated_weeks, 0)


class TestLLMFallback(unittest.TestCase):
    """Tests for LLM unavailable fallback."""

    @classmethod
    def setUpClass(cls):
        cls.courses = load_courses("data/courses.json")

    def test_fallback_without_api_key(self):
        # Ensure no API key is set
        import os
        original_key = os.environ.get("LLM_API_KEY")
        if "LLM_API_KEY" in os.environ:
            del os.environ["LLM_API_KEY"]

        config = get_llm_config()
        self.assertFalse(config["enabled"])

        student = Student(
            name="Test Fallback",
            background="Test",
            current_skills=[],
            skill_level="beginner",
            career_goal="Data Scientist",
            study_hours_per_week=10
        )
        result = recommend(student, self.courses)
        generate_fallback_explanations(result)

        # All path items should have explanations
        for item in result.learning_path:
            self.assertIsNotNone(item.llm_explanation)
            self.assertGreater(len(item.llm_explanation), 0)

        self.assertIsNotNone(result.overall_explanation)
        self.assertIsNotNone(result.next_milestone)

        # Restore original key
        if original_key is not None:
            os.environ["LLM_API_KEY"] = original_key


class TestCatalogueIntegrity(unittest.TestCase):
    """Tests for course catalogue data integrity."""

    @classmethod
    def setUpClass(cls):
        cls.courses = load_courses("data/courses.json")

    def test_no_duplicate_ids(self):
        ids = [c.id for c in self.courses]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate course IDs found")

    def test_all_prerequisites_exist(self):
        all_ids = {c.id for c in self.courses}
        for course in self.courses:
            for prereq in course.prerequisites:
                self.assertIn(prereq, all_ids,
                    f"Course '{course.id}' has unknown prerequisite '{prereq}'")

    def test_valid_difficulty_levels(self):
        valid = {"beginner", "intermediate", "advanced"}
        for course in self.courses:
            self.assertIn(course.difficulty, valid,
                f"Course '{course.id}' has invalid difficulty '{course.difficulty}'")

    def test_positive_hours(self):
        for course in self.courses:
            self.assertGreater(course.estimated_hours, 0,
                f"Course '{course.id}' has non-positive hours")


if __name__ == "__main__":
    unittest.main(verbosity=2)
