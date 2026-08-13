"""Core deterministic recommendation engine."""

from collections import defaultdict, deque
from typing import List, Dict, Set, Tuple, Optional

from models import Course, Student, PathItem, RecommendationResult


# Mapping from career goals to target skills and relevant categories
GOAL_TARGET_SKILLS = {
    "Data Scientist": {
        "target_skills": [
            "python-syntax", "pandas-dataframes", "data-cleaning", "data-transformation",
            "descriptive-statistics", "probability", "hypothesis-testing",
            "matplotlib", "seaborn", "sql-queries", "supervised-learning",
            "model-evaluation", "scikit-learn", "feature-selection",
            "time-series-modeling", "forecasting"
        ],
        "relevant_categories": {"programming", "data", "math", "machine-learning"}
    },
    "AI/ML Engineer": {
        "target_skills": [
            "python-syntax", "numpy-arrays", "pandas-dataframes",
            "descriptive-statistics", "probability", "vectors", "matrices",
            "supervised-learning", "unsupervised-learning", "model-training",
            "neural-networks", "pytorch", "cnns", "rnns",
            "model-versioning", "docker", "cloud-deployment",
            "feature-selection", "deep-rl", "cloud-ml-platforms"
        ],
        "relevant_categories": {"programming", "data", "math", "machine-learning", "deep-learning", "mlops"}
    },
    "Generative AI Developer": {
        "target_skills": [
            "python-syntax", "numpy-arrays", "pandas-dataframes",
            "supervised-learning", "model-training", "neural-networks",
            "pytorch", "backpropagation", "text-preprocessing", "tokenization",
            "word-embeddings", "transformers", "llms", "prompt-engineering",
            "fine-tuning", "rag", "generative-models", "feature-selection"
        ],
        "relevant_categories": {"programming", "data", "machine-learning", "deep-learning", "nlp", "generative-ai"}
    },
    "Machine Learning Engineer": {
        "target_skills": [
            "python-syntax", "numpy-arrays", "pandas-dataframes",
            "descriptive-statistics", "probability", "vectors", "matrices",
            "supervised-learning", "unsupervised-learning", "model-training",
            "model-evaluation", "cross-validation", "classification", "regression",
            "neural-networks", "pytorch", "model-versioning", "docker",
            "ml-ci-cd", "model-monitoring", "cloud-deployment",
            "feature-selection", "cloud-ml-platforms", "model-serving"
        ],
        "relevant_categories": {"programming", "data", "math", "machine-learning", "deep-learning", "mlops"}
    }
}

# Default target skills for unknown goals
DEFAULT_TARGET_SKILLS = [
    "python-syntax", "numpy-arrays", "pandas-dataframes",
    "descriptive-statistics", "supervised-learning", "model-training"
]

# Difficulty ordering for comparison
DIFFICULTY_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2}

# Foundational categories for beginners
FOUNDATIONAL_CATEGORIES = {"programming", "math", "tools"}


def get_target_skills(goal: str) -> Tuple[List[str], Set[str]]:
    """Get target skills and relevant categories for a career goal."""
    for key, value in GOAL_TARGET_SKILLS.items():
        if key.lower() in goal.lower() or goal.lower() in key.lower():
            return value["target_skills"], value["relevant_categories"]
    # Fallback: use default
    return DEFAULT_TARGET_SKILLS, {"programming", "data", "machine-learning"}


def calculate_skill_gaps(current_skills: List[str], target_skills: List[str]) -> List[str]:
    """Identify skills the student is missing."""
    current_set = set(s.lower().strip() for s in current_skills)
    gaps = []
    for skill in target_skills:
        skill_lower = skill.lower().strip()
        if skill_lower not in current_set:
            gaps.append(skill_lower)
    return gaps


def score_course(
    course: Course,
    missing_skills: Set[str],
    student_level: str,
    relevant_categories: Set[str],
    completed_course_ids: Set[str],
    study_hours_per_week: int = 10
) -> float:
    """
    Calculate a transparent score for a course.

    Scoring formula:
    - Skill coverage: +10 per missing skill taught by this course
    - Prerequisite satisfaction: +5 if all prerequisites are in completed_course_ids
    - Goal relevance: +3 if course category is relevant to career goal
    - Difficulty match: +2 if course difficulty <= student level + 1
    - Foundational bonus: +4 if beginner student and course is foundational category
    - Time urgency: bonus/penalty based on student study hours per week
    - Hour penalty: -0.05 per estimated hour (slight preference for efficiency)

    Parameters:
        completed_course_ids: Set of course IDs the student has already completed
        study_hours_per_week: Student available study time (affects time-urgency weighting)
    """
    # Skill coverage score
    skills_covered = set(course.skills_taught) & missing_skills
    skill_score = len(skills_covered) * 10.0

    # Prerequisite satisfaction
    prereq_set = set(course.prerequisites)
    if prereq_set.issubset(completed_course_ids):
        prereq_score = 5.0
    else:
        prereq_score = -10.0  # Strong penalty for unmet prerequisites

    # Goal relevance
    if course.category in relevant_categories:
        relevance_score = 3.0
    else:
        relevance_score = 0.0

    # Difficulty match
    student_diff = DIFFICULTY_ORDER.get(student_level, 0)
    course_diff = DIFFICULTY_ORDER.get(course.difficulty, 0)
    if course_diff <= student_diff + 1:
        difficulty_score = 2.0
    else:
        difficulty_score = -3.0  # Penalty for being too advanced

    # Foundational bonus for beginners
    if student_level == "beginner" and course.category in FOUNDATIONAL_CATEGORIES:
        foundational_bonus = 4.0
    else:
        foundational_bonus = 0.0

    # Time urgency weighting
    if study_hours_per_week <= 5:
        # Low study time: favor shorter courses significantly
        time_bonus = max(0, 25 - course.estimated_hours) * 0.4
    elif study_hours_per_week >= 25:
        # High study time: slight preference for comprehensive (longer) courses
        time_bonus = course.estimated_hours * 0.02
    else:
        time_bonus = 0.0

    # Hour penalty (slight)
    hour_penalty = course.estimated_hours * 0.05

    total = skill_score + prereq_score + relevance_score + difficulty_score + foundational_bonus + time_bonus - hour_penalty
    return total


def build_prerequisite_aware_path(
    selected_courses: List[Course],
    all_courses: Dict[str, Course]
) -> List[Course]:
    """
    Ensure all prerequisites are included and order courses topologically.
    Uses Kahn's algorithm for topological sort.
    """
    # Build the set of all required courses (selected + their prerequisites)
    required_ids = set()
    for course in selected_courses:
        required_ids.add(course.id)
        # Recursively add prerequisites
        queue = list(course.prerequisites)
        while queue:
            prereq_id = queue.pop(0)
            if prereq_id not in required_ids:
                required_ids.add(prereq_id)
                if prereq_id in all_courses:
                    queue.extend(all_courses[prereq_id].prerequisites)

    # Build adjacency list and in-degree count
    required_courses = [all_courses[cid] for cid in required_ids if cid in all_courses]
    in_degree = {c.id: 0 for c in required_courses}
    adj = defaultdict(list)

    for course in required_courses:
        for prereq_id in course.prerequisites:
            if prereq_id in required_ids:
                adj[prereq_id].append(course.id)
                in_degree[course.id] += 1

    # Kahn's algorithm
    queue = deque([cid for cid, deg in in_degree.items() if deg == 0])
    ordered_ids = []

    while queue:
        # Sort by difficulty then by ID for deterministic ordering
        queue = deque(sorted(queue, key=lambda x: (
            DIFFICULTY_ORDER.get(all_courses[x].difficulty, 0),
            all_courses[x].estimated_hours,
            x
        )))
        cid = queue.popleft()
        ordered_ids.append(cid)
        for neighbor in adj[cid]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(ordered_ids) != len(required_courses):
        raise ValueError("Cycle detected in course prerequisites!")

    return [all_courses[cid] for cid in ordered_ids]


def generate_deterministic_reason(
    course: Course,
    missing_skills: Set[str],
    student: Student,
    all_courses: Dict[str, Course]
) -> str:
    """Generate a deterministic explanation for why a course was selected."""
    reasons = []

    # Check if this course teaches missing skills
    skills_covered = set(course.skills_taught) & missing_skills
    if skills_covered:
        skills_list = ", ".join(sorted(skills_covered))
        reasons.append(f"Teaches missing skills: {skills_list}")

    # Check if it's a prerequisite for another selected course
    is_prereq_for = []
    for other_course in all_courses.values():
        if course.id in other_course.prerequisites:
            is_prereq_for.append(other_course.title)

    if is_prereq_for and not skills_covered:
        reasons.append(f"Required prerequisite for: {", ".join(is_prereq_for[:2])}")
    elif is_prereq_for:
        reasons.append(f"Also prerequisite for: {", ".join(is_prereq_for[:2])}")

    # Difficulty context
    if course.difficulty == "beginner" and student.skill_level == "beginner":
        reasons.append("Appropriate beginner-level foundation")
    elif course.difficulty == "advanced":
        reasons.append("Advanced course for specialization")

    if not reasons:
        reasons.append("Builds foundational knowledge for your goal")

    return "; ".join(reasons)


def recommend(student: Student, courses: List[Course]) -> RecommendationResult:
    """
    Main recommendation function.

    Pipeline:
    1. Identify target skills from career goal
    2. Calculate missing skills
    3. Score and select courses to cover missing skills (greedy)
    4. Resolve prerequisites and build ordered path
    5. Generate deterministic explanations
    """
    all_courses = {c.id: c for c in courses}
    all_skills = set()
    for c in courses:
        all_skills.update(c.skills_taught)

    # Step 1 & 2: Target skills and gaps
    target_skills, relevant_categories = get_target_skills(student.career_goal)
    skill_gaps = calculate_skill_gaps(student.current_skills, target_skills)
    missing_skills = set(skill_gaps)

    # Step 3: Select courses greedily to cover missing skills
    student_skill_set = set(s.lower().strip() for s in student.current_skills)

    # Track both skills gained AND course IDs completed (for prerequisite checking)
    satisfied_skills = set(student_skill_set)
    completed_course_ids = set()
    selected_courses = []
    covered_skills = set()

    # Iteratively select best course until all skills are covered or no more useful courses
    max_iterations = 50
    iteration = 0

    while missing_skills - covered_skills and iteration < max_iterations:
        iteration += 1
        best_course = None
        best_score = float('-inf')

        for course in courses:
            if course in selected_courses:
                continue

            # Check if this course teaches any remaining missing skills
            remaining_missing = missing_skills - covered_skills
            skills_this_covers = set(course.skills_taught) & remaining_missing

            # Also consider courses that are prerequisites for high-value courses
            if not skills_this_covers:
                is_needed_prereq = False
                for other in courses:
                    if other.id == course.id:
                        continue
                    other_skills = set(other.skills_taught) & remaining_missing
                    if other_skills and course.id in other.prerequisites:
                        is_needed_prereq = True
                        break
                if not is_needed_prereq:
                    continue

            score = score_course(
                course,
                remaining_missing,
                student.skill_level,
                relevant_categories,
                completed_course_ids,
                study_hours_per_week=student.study_hours_per_week
            )

            if score > best_score:
                best_score = score
                best_course = course

        if best_course is None:
            break

        selected_courses.append(best_course)
        covered_skills.update(best_course.skills_taught)
        satisfied_skills.update(best_course.skills_taught)
        completed_course_ids.add(best_course.id)

    # Step 4: Build prerequisite-aware ordered path
    ordered_courses = build_prerequisite_aware_path(selected_courses, all_courses)

    # Step 5: Generate path items with deterministic reasons
    learning_path = []
    total_hours = 0

    for i, course in enumerate(ordered_courses, 1):
        reason = generate_deterministic_reason(
            course,
            missing_skills,
            student,
            all_courses
        )
        learning_path.append(PathItem(
            order=i,
            course=course,
            reason=reason
        ))
        total_hours += course.estimated_hours

    # Calculate estimated weeks
    estimated_weeks = total_hours / student.study_hours_per_week if student.study_hours_per_week > 0 else 0

    # Determine next milestone
    next_milestone = None
    if learning_path:
        next_milestone = f"Complete '{learning_path[0].course.title}' to establish foundational skills"

    return RecommendationResult(
        student=student,
        target_skills=target_skills,
        skill_gaps=skill_gaps,
        learning_path=learning_path,
        total_hours=total_hours,
        estimated_weeks=round(estimated_weeks, 1),
        next_milestone=next_milestone
    )
