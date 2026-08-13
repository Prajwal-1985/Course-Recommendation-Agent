#  Course Recommendation Agent

### ROOMAN TECHNOLOGIES · Junior AI Research Associate · 24-Hour AI Agent Challenge

> **An AI-powered learning-path planner that analyzes a student's background, skills, career goal, and available study time to generate a structured and personalized course roadmap.**

---

##  Overview

Choosing what to learn next can be difficult when a learner has a broad career goal but doesn't know which skills or courses should come first.

The **Course Recommendation Agent** addresses this problem by combining:

*  Skill-gap analysis
*  Career-goal relevance
*  Course catalogue data
*  Prerequisite-aware recommendations
*  Optional LLM-powered personalization
*  Deterministic fallback explanations

Instead of simply generating a list of courses, the agent produces an **ordered learning path** and explains why each recommendation is relevant.

---

#  Key Features

| Feature                        | Description                                                      |
| ------------------------------ | ---------------------------------------------------------------- |
|  Personalized Learning Paths | Generates recommendations based on the learner's profile         |
|  Skill Gap Analysis          | Identifies skills that need to be developed                      |
|  Prerequisite Awareness      | Considers course dependencies when creating the roadmap          |
|  Structured Recommendations  | Provides course, category, difficulty, duration, and reasoning   |
|  LLM Enhancement             | Generates personalized explanations when an LLM API is available |
|  Graceful Fallback          | Continues working without an LLM API key                         |
|  Interactive CLI             | Allows users to enter their own profile                          |
|  Demo Mode                   | Runs recommendations for all sample students                     |
|  JSON Output                 | Saves structured recommendation results                          |
|  Text Output                 | Saves human-readable recommendation reports                      |

---

#  How It Works

```text
┌─────────────────────┐
│   Student Profile   │
│                     │
│ Background          │
│ Current Skills      │
│ Skill Level         │
│ Career Goal         │
│ Study Time          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Input Validation    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Skill Gap Analysis  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Course Recommendation│
│      Engine         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Prerequisite        │
│ Resolution          │
└──────────┬──────────┘
           │
           ▼
      ┌────┴────┐
      │         │
      ▼         ▼
  LLM API    Fallback
      │         │
      └────┬────┘
           ▼
┌─────────────────────┐
│ Personalized        │
│ Learning Path       │
└─────────────────────┘
```

The application first generates the recommendation using the core recommendation engine and then enhances the result with the optional LLM layer. If the LLM is unavailable, the application continues using deterministic explanations.

---

#  Hybrid AI Architecture

The project intentionally separates **recommendation logic** from **natural-language generation**.

### Deterministic Layer

The recommendation engine is responsible for deciding:

> **What should the student learn?**

This makes the core recommendation process more predictable and testable.

### LLM Layer

The LLM is used to enhance the recommendation with:

> **Why is this course useful for this student?**

The application calls the LLM enhancement layer after generating the recommendation.

### Fallback Layer

An important design choice is that an LLM API is **not required for the application to function**.

Without `LLM_API_KEY`, the agent uses deterministic explanations instead.

This makes the project easier for evaluators to run and test.

---

#  Student Input

The interactive agent collects:

```text
Name
Background
Current skills
Skill level
Career goal
Study hours per week
```

For example:

```text
Name: Arjun

Background:
B.Tech Computer Science student

Current skills:
Python, SQL, HTML

Skill level:
Intermediate

Career goal:
AI/ML Engineer

Study hours per week:
15
```

The application converts this information into a structured student profile before processing the recommendation.

---

#  Recommendation Output

For every learner, the agent provides:

### Student Profile

* Name
* Background
* Skill level
* Career goal
* Available study time

### Identified Skill Gaps

The agent lists skills that should be developed.

### Recommended Learning Path

Each recommendation contains:

* Course title
* Category
* Difficulty
* Estimated duration
* Deterministic reasoning
* Optional personalized LLM explanation

These fields are directly displayed by the CLI application.

### Summary

The final recommendation includes:

* Total number of courses
* Total learning time
* Estimated duration in weeks
* Overall strategy
* Next milestone

---

#  Application Modes

The agent provides three command-line modes.

## 1. Interactive Mode

Run:

```bash
python app.py
```

or:

```bash
python app.py --interactive
```

This allows a user to enter a custom student profile interactively.

---

## 2. Demo Mode

Run:

```bash
python app.py --demo
```

The application loads the sample student profiles and generates recommendations for each of them.

This mode is particularly useful for recruiters and evaluators because the project can be demonstrated without manually entering student information.

---

## 3. Help

Run:

```bash
python app.py --help
```

Available options include:

```text
--interactive, -i
--demo, -d
--help, -h
```
## Web UI (Streamlit)

A professional web interface with Light/Dark theme toggle, interactive timeline, and skill gap visualization.

```bash
python -m streamlit run web_app.py
```
Features: Light/Dark theme toggle, interactive timeline, skill gap visualization, JSON export.

---

#  Output Generation

The agent can save recommendation results in two formats.

### JSON

Structured output is saved under:

```text
outputs/
```

The JSON contains information including:

* Student profile
* Target skills
* Skill gaps
* Course IDs
* Course titles
* Categories
* Difficulty
* Estimated hours
* Recommendation reasoning
* Personalized explanations
* Total learning time
* Estimated weeks
* Overall explanation
* Next milestone

### Text

A human-readable `.txt` version is also generated for each saved recommendation.

---

#  Project Structure

```text
course-recommendation-agent/
│
├── app.py
├── recommender.py
├── web_app.py
├── llm.py
├── models.py
├── utils.py
│
├── data/
│   ├── courses.json
│   └── sample_students.json
│
├── outputs/
│   └── generated recommendations
│
├── tests/
│   └── test_recommender.py
│
├── samples/
│   └── sample inputs/outputs
│
├── requirements.txt
├── .env.example
├── .gitignore
├── AGENTS.md
└── README.md
```

### Core Components

| Component                   | Responsibility                                      |
| --------------------------- | --------------------------------------------------- |
| `app.py`                    | CLI entry point and application workflow            |
| `recommender.py`            | Core recommendation logic                           |
| `llm.py`                    | LLM integration and fallback behavior               |
| `models.py`                 | Student and recommendation data models              |
| `utils.py`                  | Catalogue loading, validation, and helper functions |
| `data/courses.json`         | Course catalogue                                    |
| `data/sample_students.json` | Sample learners                                     |
| `tests/`                    | Automated tests                                     |

---

#  Requirements

* Python 3.11+
* `pip`
* Internet connection only when using the optional LLM service
* Optional LLM API key

---

#  Installation

## Clone the Repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd course-recommendation-agent
```

## Create a Virtual Environment

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

#  LLM Configuration

The LLM component is optional.

Configure the required environment variables using the project's `.env.example` file.

The application supports:

```text
LLM_API_KEY
LLM_BASE_URL
LLM_MODEL
```

The default LLM base URL and model are defined by the application configuration.

### Security

**Never commit API keys to GitHub.**

Make sure:

```text
.env
```

is included in `.gitignore`.

Use:

```text
.env.example
```

to document the required configuration without exposing credentials.

---

#  Testing

The project includes automated tests for the recommendation engine.

Run:

```bash
python -m pytest tests/test_recommender.py -v
```

The tests should be run before submitting the repository to ensure the recommendation logic remains stable.

---

#  Design Philosophy

The project follows three principles:

### 01 — Explainability

A recommendation system should not simply produce an unexplained list.

The agent exposes:

```text
Student → Skill Gaps → Recommended Courses → Reasoning
```

### 02 — Reliability

The application should continue functioning even when an external LLM service is unavailable.

### 03 — Separation of Responsibilities

The recommendation engine and language-generation layer have separate responsibilities.

```text
Recommendation Engine
        │
        │ Determines courses
        ▼
Learning Path
        │
        │ Optional personalization
        ▼
LLM Explanation
```

This keeps the system easier to understand, test, and maintain.

---

#  Engineering Tradeoffs

| Decision                           | Advantage                         | Tradeoff                                        |
| ---------------------------------- | --------------------------------- | ----------------------------------------------- |
| Local course catalogue             | Reproducible and easy to evaluate | Course data is not real-time                    |
| Deterministic recommendation logic | Transparent and testable          | Less adaptive than a learned recommender        |
| Optional LLM                       | Adds natural personalization      | Requires external API for enhanced explanations |
| CLI + Streamlit Web UI             | Fast CLI for evaluators, rich web UI for demos | Requires streamlit dependency      |
| JSON data storage                  | Simple and portable               | Not intended for large-scale datasets           |

---

#  Current Limitations

The current implementation is intentionally scoped for a 24-hour AI agent challenge.

Potential limitations include:

* The course catalogue is locally maintained.
* Recommendation quality depends on the quality of the catalogue and scoring logic.
* LLM personalization depends on external API availability.
* No database persistence between sessions.
* Recommendations are not persisted between sessions.

These are deliberate scope decisions intended to prioritize a **working, explainable, reproducible agent** over unnecessary complexity.

---

#  Future Improvements

With additional development time, the agent could be extended with:

###  Web Interface

###  Enhanced Visualizations

Charts showing skill coverage, learning velocity, and career trajectory over time.

###  Semantic Skill Matching

Embeddings could be introduced to understand relationships between skills expressed in different ways.

###  Adaptive Recommendations

Student feedback and completed courses could be used to continuously update the learning path.

###  Live Course Sources

External course APIs could provide:

* Current course availability
* Course ratings
* Providers
* Updated learning content

###  Persistent Learner Profiles

A database could store:

* Completed courses
* Current skills
* Previous recommendations
* Learning progress

---

#  Rooman Challenge Deliverables

This project targets the required deliverables for the **Course Recommendation Agent**:

| Challenge Requirement           | Project Implementation           |
| ------------------------------- | -------------------------------- |
| Course catalogue                | `data/courses.json`              |
| 3–4 sample student profiles     | `data/sample_students.json`      |
| Recommended learning paths      | Recommendation engine            |
| Rationale for recommendations   | Deterministic + LLM explanations |
| Runnable agent                  | `app.py`                         |
| Sample outputs                  | `outputs/` / `samples/`          |
| Scoring/recommendation approach | `recommender.py` + documentation |
| README                          | This document                    |
| Tradeoff notes                  | Included above                   |

---

#  Pre-Submission Checklist

Before submitting the GitHub repository:

```text
☐ Application runs successfully
☐ Interactive mode tested
☐ Demo mode tested
☐ Automated tests pass
☐ Course catalogue included
☐ Sample student profiles included
☐ Sample outputs included
☐ README completed
☐ requirements.txt verified
☐ .env excluded from Git
☐ No API keys committed
☐ Repository is public
☐ GitHub clone + setup instructions tested
☐ Final repository URL opens correctly
```

---

#  What I Learned From This Project

This project demonstrates practical experience with:

* Python application development
* AI agent architecture
* Recommendation systems
* Rule-based decision making
* Skill-gap analysis
* LLM integration
* API configuration
* Fallback engineering
* CLI application design
* Automated testing
* Structured data processing
* Git/GitHub-based project delivery

---

#  Project

**Course Recommendation Agent**

Built for:

**ROOMAN TECHNOLOGIES**
**Junior AI Research Associate — 24-Hour AI Agent Challenge**

### Technology

```text
Python
JSON
Recommendation Logic
LLM API
CLI
Automated Testing
```

---

##  License

This project is released under the **MIT License**.
