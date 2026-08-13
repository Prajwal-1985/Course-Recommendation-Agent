import streamlit as st
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Student
from utils import load_courses, get_all_skills_from_courses, validate_student
from recommender import recommend
from llm import enhance_with_llm

st.set_page_config(
    page_title="Course Recommendation Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# THEME MANAGEMENT
# =============================================================================
def get_theme_css(theme: str) -> str:
    if theme == "Dark":
        return """
        <style>
            :root {
                --bg-primary: #0e1117;
                --bg-secondary: #1a1d24;
                --bg-card: #21242b;
                --text-primary: #e6e6e6;
                --text-secondary: #a0a0a0;
                --accent: #4dabf7;
                --accent-light: #74c0fc;
                --success: #51cf66;
                --warning: #ffd43b;
                --danger: #ff6b6b;
                --border: #2d333b;
                --shadow: rgba(0,0,0,0.4);
            }
            .stApp { background-color: var(--bg-primary); }
            .stSidebar { background-color: var(--bg-secondary) !important; }
            .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span { color: var(--text-primary) !important; }
            .stSelectbox label, .stSlider label, .stTextInput label, .stTextArea label { color: var(--text-primary) !important; }
            div[data-testid="stMetricValue"] { color: var(--accent) !important; }
            div[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }
            .stExpander { background-color: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; }
            .stButton>button { background: linear-gradient(135deg, #4dabf7, #339af0) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
            .stButton>button:hover { background: linear-gradient(135deg, #74c0fc, #4dabf7) !important; }
            hr { border-color: var(--border) !important; }
            .stInfo { background-color: rgba(77, 171, 247, 0.15) !important; border-left-color: var(--accent) !important; }
            .stSuccess { background-color: rgba(81, 207, 102, 0.15) !important; border-left-color: var(--success) !important; }
            .stWarning { background-color: rgba(255, 212, 59, 0.15) !important; border-left-color: var(--warning) !important; }
        </style>
        """
    else:
        return """
        <style>
            :root {
                --bg-primary: #f8f9fa;
                --bg-secondary: #ffffff;
                --bg-card: #ffffff;
                --text-primary: #212529;
                --text-secondary: #6c757d;
                --accent: #1971c2;
                --accent-light: #339af0;
                --success: #2b8a3e;
                --warning: #f08c00;
                --danger: #c92a2a;
                --border: #dee2e6;
                --shadow: rgba(0,0,0,0.08);
            }
            .stApp { background-color: var(--bg-primary); }
            .stSidebar { background-color: var(--bg-secondary) !important; }
            .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span { color: var(--text-primary) !important; }
            .stSelectbox label, .stSlider label, .stTextInput label, .stTextArea label { color: var(--text-primary) !important; }
            div[data-testid="stMetricValue"] { color: var(--accent) !important; }
            div[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }
            .stExpander { background-color: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; }
            .stButton>button { background: linear-gradient(135deg, #1971c2, #1864ab) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
            .stButton>button:hover { background: linear-gradient(135deg, #339af0, #1971c2) !important; }
            hr { border-color: var(--border) !important; }
            .stInfo { background-color: rgba(25, 113, 194, 0.08) !important; border-left-color: var(--accent) !important; }
            .stSuccess { background-color: rgba(43, 138, 62, 0.08) !important; border-left-color: var(--success) !important; }
            .stWarning { background-color: rgba(240, 140, 0, 0.08) !important; border-left-color: var(--warning) !important; }
        </style>
        """

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

shared_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    .gradient-header {
        background: linear-gradient(135deg, var(--accent), var(--accent-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 2.8rem;
        letter-spacing: -1.5px;
        margin-bottom: 0.3rem;
    }
    .subtitle { color: var(--text-secondary); font-size: 1.05rem; font-weight: 400; margin-bottom: 2rem; }

    .hero-card {
        background: linear-gradient(135deg, var(--accent), var(--accent-light));
        border-radius: 20px;
        padding: 2.5rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(25, 113, 194, 0.25);
    }
    .hero-card h2 { color: white !important; margin: 0 0 0.5rem 0; font-size: 1.8rem; }
    .hero-card p { color: rgba(255,255,255,0.9) !important; margin: 0; font-size: 1rem; }

    .metric-container {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 2px 12px var(--shadow);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-container:hover { transform: translateY(-3px); box-shadow: 0 6px 20px var(--shadow); }
    .metric-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: var(--accent); line-height: 1; }
    .metric-label { font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.4rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }

    .timeline-line {
        position: absolute;
        left: 18px;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(to bottom, var(--accent), var(--accent-light));
        border-radius: 3px;
    }
    .timeline-wrapper { position: relative; padding-left: 48px; }
    .timeline-item { position: relative; margin-bottom: 1.2rem; }
    .timeline-dot {
        position: absolute;
        left: -38px;
        top: 18px;
        width: 14px;
        height: 14px;
        background: var(--accent);
        border: 3px solid var(--bg-primary);
        border-radius: 50%;
        box-shadow: 0 0 0 3px var(--accent);
    }
    .course-card {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 2px 12px var(--shadow);
        transition: all 0.3s ease;
    }
    .course-card:hover { box-shadow: 0 8px 24px var(--shadow); transform: translateX(4px); }
    .course-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, var(--accent), var(--accent-light));
        color: white;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 0.8rem;
    }
    .course-title { font-size: 1.15rem; font-weight: 600; color: var(--text-primary); }
    .course-meta { display: flex; gap: 1rem; margin-top: 0.6rem; font-size: 0.85rem; color: var(--text-secondary); }
    .difficulty-badge {
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-beginner { background: rgba(43, 138, 62, 0.15); color: #2b8a3e; }
    .badge-intermediate { background: rgba(240, 140, 0, 0.15); color: #f08c00; }
    .badge-advanced { background: rgba(201, 42, 42, 0.15); color: #c92a2a; }

    .skill-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(201, 42, 42, 0.1);
        color: #c92a2a;
        border: 1px solid rgba(201, 42, 42, 0.2);
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    .skill-pill::before { content: "⚡"; font-size: 0.7rem; }

    .insight-box {
        background: linear-gradient(135deg, rgba(77, 171, 247, 0.08), rgba(51, 154, 240, 0.05));
        border-left: 3px solid var(--accent);
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-top: 0.5rem;
    }
    .strategy-card {
        background: linear-gradient(135deg, rgba(77, 171, 247, 0.08), rgba(51, 154, 240, 0.05));
        border: 1px solid rgba(77, 171, 247, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
    }
    .milestone-card {
        background: linear-gradient(135deg, rgba(43, 138, 62, 0.08), rgba(43, 138, 62, 0.05));
        border: 1px solid rgba(43, 138, 62, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
    }
    .progress-container {
        background: var(--bg-secondary);
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--accent), var(--accent-light));
        border-radius: 10px;
        transition: width 0.8s ease;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .footer {
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.8rem;
        margin-top: 3rem;
        padding: 1.5rem;
        border-top: 1px solid var(--border);
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in { animation: fadeIn 0.5s ease forwards; }
</style>
"""

st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)
st.markdown(shared_css, unsafe_allow_html=True)

# =============================================================================
# LOAD DATA
# =============================================================================
try:
    courses = load_courses("data/courses.json")
    all_skills = sorted(get_all_skills_from_courses(courses))
except Exception as e:
    st.error(f"Failed to load course catalogue: {e}")
    st.stop()

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    theme_choice = st.radio(
        "Theme", ["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1,
        horizontal=True, key="theme_radio"
    )
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    st.divider()
    st.markdown("### 👤 Student Profile")

    sample_option = st.selectbox(
        "📋 Quick Load Sample",
        ["None", "Riya Sharma → Data Scientist", 
         "Arjun Patel → AI/ML Engineer",
         "Neha Gupta → Generative AI",
         "Karthik Iyer → ML Engineer",
         "Ananya Reddy → ML Engineer"]
    )

    st.divider()
    name = st.text_input("📝 Name", placeholder="e.g., Alex Kumar", value="")
    background = st.text_area("💼 Background", placeholder="e.g., B.Tech CSE student in 3rd year", height=80, value="")

    col1, col2 = st.columns(2)
    with col1:
        skill_level = st.selectbox("📊 Level", ["beginner", "intermediate", "advanced"])
    with col2:
        study_hours = st.number_input("⏱ Hours/Week", min_value=1, max_value=60, value=10)

    career_goal = st.selectbox(
        "🎯 Career Goal",
        ["Data Scientist", "AI/ML Engineer", "Generative AI Developer", "Machine Learning Engineer"]
    )

    st.markdown("### 🛠 Skills")
    current_skills = st.multiselect(
        "Select your current skills", all_skills,
        help="Leave empty if starting from scratch", label_visibility="collapsed"
    )

    st.divider()
    run_btn = st.button("🚀 Generate Path", type="primary", use_container_width=True)

# =============================================================================
# LOAD SAMPLE DATA
# =============================================================================
if sample_option != "None":
    from utils import load_sample_students
    samples = load_sample_students("data/sample_students.json")
    sample_map = {
        "Riya Sharma → Data Scientist": "Riya Sharma",
        "Arjun Patel → AI/ML Engineer": "Arjun Patel",
        "Neha Gupta → Generative AI": "Neha Gupta",
        "Karthik Iyer → ML Engineer": "Karthik Iyer",
        "Ananya Reddy → ML Engineer": "Ananya Reddy"
    }
    selected = next((s for s in samples if s.name == sample_map[sample_option]), None)
    if selected:
        name = selected.name
        background = selected.background
        skill_level = selected.skill_level
        career_goal = selected.career_goal
        study_hours = selected.study_hours_per_week
        current_skills = selected.current_skills

# =============================================================================
# MAIN CONTENT
# =============================================================================
st.markdown('<div class="gradient-header">🎓 Course Recommendation Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">ROOMAN AI CHALLENGE — Intelligent, Prerequisite-Aware Learning Paths</div>', unsafe_allow_html=True)

if not run_btn:
    st.markdown("""
    <div class="hero-card animate-in">
        <h2>Welcome to Your AI Learning Advisor</h2>
        <p>Enter your profile in the sidebar and generate a personalized, ordered learning path 
        backed by deterministic scoring and optional LLM explanations.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-container"><div class="metric-icon">📚</div><div class="metric-value">{len(courses)}</div><div class="metric-label">Courses</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-container"><div class="metric-icon">🎯</div><div class="metric-value">4</div><div class="metric-label">Career Tracks</div></div>', unsafe_allow_html=True)
    with col3:
        cats = len(set(c.category for c in courses))
        st.markdown(f'<div class="metric-container"><div class="metric-icon">📂</div><div class="metric-value">{cats}</div><div class="metric-label">Categories</div></div>', unsafe_allow_html=True)

    st.markdown("### How It Works")
    steps = [
        ("1️⃣", "Profile Input", "Tell us your background, skills, goal, and available study time."),
        ("2️⃣", "Skill Gap Analysis", "We identify exactly what you need to learn to reach your goal."),
        ("3️⃣", "Smart Scoring", "Courses are ranked by relevance, prerequisites, difficulty match, and time efficiency."),
        ("4️⃣", "Ordered Path", "Kahn's topological sort guarantees prerequisites always come first."),
        ("5️⃣", "Personalized Explanations", "LLM-enhanced rationales explain why each course fits YOU.")
    ]
    for emoji, title, desc in steps:
        c1, c2 = st.columns([0.08, 0.92])
        with c1:
            st.markdown(f"<h3 style='margin:0;'>{emoji}</h3>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"**{title}** — {desc}")

    st.markdown("### Available Career Tracks")
    tracks = [
        ("🧮", "Data Scientist", "Python → SQL → Pandas → Stats → ML → Visualization"),
        ("🤖", "AI/ML Engineer", "Python → Math → ML → Deep Learning → MLOps"),
        ("✨", "Generative AI Developer", "Python → ML → Deep Learning → NLP → LLMs → GenAI"),
        ("⚙️", "Machine Learning Engineer", "Python → ML → Deep Learning → MLOps → Cloud Deployment")
    ]
    for icon, title, path in tracks:
        with st.expander(f"{icon} {title}"):
            st.caption(f"Typical path: {path}")

    st.markdown("<div class='footer'>Built for the ROOMAN AI CHALLENGE — Junior AI Research Associate 24-Hour AI Agent Challenge</div>", unsafe_allow_html=True)
    st.stop()

# =============================================================================
# GENERATE RECOMMENDATION
# =============================================================================
if not name or not background:
    st.warning("Please enter your name and background in the sidebar.")
    st.stop()

student = Student(
    name=name, background=background, current_skills=current_skills,
    skill_level=skill_level.lower(), career_goal=career_goal,
    study_hours_per_week=int(study_hours)
)

warnings = validate_student(student, set(all_skills))
for w in warnings:
    st.warning(w)

with st.spinner("🔍 Analyzing skill gaps and building your personalized path..."):
    result = recommend(student, courses)
    enhance_with_llm(result)

# =============================================================================
# RESULTS DASHBOARD
# =============================================================================
st.markdown("<div class='section-header'>📊 Profile Overview</div>", unsafe_allow_html=True)

pc1, pc2, pc3, pc4 = st.columns(4)
with pc1:
    st.markdown(f'<div class="metric-container animate-in"><div class="metric-icon">👤</div><div class="metric-value" style="font-size:1.3rem;">{result.student.name}</div><div class="metric-label">{result.student.skill_level.title()}</div></div>', unsafe_allow_html=True)
with pc2:
    st.markdown(f'<div class="metric-container animate-in"><div class="metric-icon">🎯</div><div class="metric-value" style="font-size:1.3rem;">{result.student.career_goal}</div><div class="metric-label">Career Goal</div></div>', unsafe_allow_html=True)
with pc3:
    gap_count = len(result.skill_gaps)
    st.markdown(f'<div class="metric-container animate-in"><div class="metric-icon">⚡</div><div class="metric-value">{gap_count}</div><div class="metric-label">Skill Gaps</div></div>', unsafe_allow_html=True)
with pc4:
    st.markdown(f'<div class="metric-container animate-in"><div class="metric-icon">⏱</div><div class="metric-value">{result.student.study_hours_per_week}h</div><div class="metric-label">Per Week</div></div>', unsafe_allow_html=True)

if result.skill_gaps:
    st.markdown("<div class='section-header'>🎯 Identified Skill Gaps</div>", unsafe_allow_html=True)
    pills_html = " ".join([f'<span class="skill-pill">{gap}</span>' for gap in result.skill_gaps])
    st.markdown(f"<div class='animate-in'>{pills_html}</div>", unsafe_allow_html=True)

    total_target = len(result.target_skills)
    acquired = total_target - len(result.skill_gaps)
    pct = int((acquired / total_target) * 100) if total_target > 0 else 0
    st.markdown(f"""
    <div style="margin-top:1rem;">
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:var(--text-secondary);">
            <span>Progress toward {result.student.career_goal}</span>
            <span>{acquired}/{total_target} skills ({pct}%)</span>
        </div>
        <div class="progress-container"><div class="progress-fill" style="width: {pct}%;"></div></div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.success("✅ No skill gaps identified — you have a strong foundation for this goal!")

st.divider()

# =============================================================================
# LEARNING PATH TIMELINE — RENDER EACH CARD INDIVIDUALLY (NO GIANT HTML BLOB)
# =============================================================================
st.markdown("<div class='section-header'>📚 Recommended Learning Path</div>", unsafe_allow_html=True)
st.caption("Courses are ordered topologically — prerequisites always appear before dependent courses.")

# Start timeline wrapper
st.markdown('<div class="timeline-wrapper animate-in"><div class="timeline-line"></div>', unsafe_allow_html=True)

for item in result.learning_path:
    diff_class = f"badge-{item.course.difficulty}"

    # Build each card as a single-line HTML string to avoid indentation issues
    card_html = f'<div class="timeline-item"><div class="timeline-dot"></div><div class="course-card">'
    card_html += f'<div style="display:flex;align-items:center;flex-wrap:wrap;gap:0.5rem;"><span class="course-number">{item.order}</span><span class="course-title">{item.course.title}</span><span class="difficulty-badge {diff_class}">{item.course.difficulty}</span></div>'
    card_html += f'<div class="course-meta"><span>📂 {item.course.category}</span><span>⏱ {item.course.estimated_hours}h</span><span>🛠 {len(item.course.skills_taught)} skills</span></div>'
    card_html += f'<div style="margin-top:0.8rem;padding-top:0.8rem;border-top:1px solid var(--border);"><div style="font-size:0.9rem;color:var(--text-secondary);margin-bottom:0.4rem;"><strong style="color:var(--text-primary);">Why selected:</strong> {item.reason}</div>'

    if item.llm_explanation:
        card_html += f'<div class="insight-box"><span style="font-size:0.9rem;color:var(--text-primary);">💡 {item.llm_explanation}</span></div>'

    card_html += f'<div style="margin-top:0.6rem;font-size:0.82rem;color:var(--text-secondary);"><strong>Skills gained:</strong> {', '.join(item.course.skills_taught)}</div></div></div></div>'

    st.markdown(card_html, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# =============================================================================
# SUMMARY METRICS
# =============================================================================
st.markdown("<div class='section-header'>📈 Journey Summary</div>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="metric-container animate-in"><div class="metric-icon">📚</div><div class="metric-value">{len(result.learning_path)}</div><div class="metric-label">Courses</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-container animate-in"><div class="metric-icon">⏳</div><div class="metric-value">{result.total_hours}</div><div class="metric-label">Total Hours</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-container animate-in"><div class="metric-icon">📅</div><div class="metric-value">{result.estimated_weeks}</div><div class="metric-label">Est. Weeks</div></div>', unsafe_allow_html=True)
with m4:
    avg = round(result.total_hours / len(result.learning_path), 1) if result.learning_path else 0
    st.markdown(f'<div class="metric-container animate-in"><div class="metric-icon">📊</div><div class="metric-value">{avg}h</div><div class="metric-label">Avg / Course</div></div>', unsafe_allow_html=True)

col_strat, col_mile = st.columns(2)
with col_strat:
    if result.overall_explanation:
        st.markdown(f'<div class="strategy-card animate-in"><div style="font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;color:var(--accent);">🧠 Learning Strategy</div><div style="color:var(--text-primary);line-height:1.6;">{result.overall_explanation}</div></div>', unsafe_allow_html=True)
with col_mile:
    if result.next_milestone:
        st.markdown(f'<div class="milestone-card animate-in"><div style="font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;color:var(--success);">🎯 Next Milestone</div><div style="color:var(--text-primary);line-height:1.6;">{result.next_milestone}</div></div>', unsafe_allow_html=True)

st.divider()

# =============================================================================
# DOWNLOAD & FOOTER
# =============================================================================
json_data = {
    "student": {
        "name": result.student.name, "background": result.student.background,
        "current_skills": result.student.current_skills, "skill_level": result.student.skill_level,
        "career_goal": result.student.career_goal, "study_hours_per_week": result.student.study_hours_per_week
    },
    "target_skills": result.target_skills, "skill_gaps": result.skill_gaps,
    "learning_path": [
        {
            "order": item.order, "course_id": item.course.id, "title": item.course.title,
            "category": item.course.category, "difficulty": item.course.difficulty,
            "estimated_hours": item.course.estimated_hours, "skills_taught": item.course.skills_taught,
            "deterministic_reason": item.reason, "personalized_explanation": item.llm_explanation
        }
        for item in result.learning_path
    ],
    "total_hours": result.total_hours, "estimated_weeks": result.estimated_weeks,
    "overall_explanation": result.overall_explanation, "next_milestone": result.next_milestone
}

safe_name = result.student.name.lower().replace(" ", "_").replace("/", "_")
col_dl, _ = st.columns([1, 3])
with col_dl:
    st.download_button(
        label="📥 Download Full Report (JSON)",
        data=json.dumps(json_data, indent=2, ensure_ascii=False),
        file_name=f"{safe_name}_learning_path.json",
        mime="application/json", use_container_width=True
    )

st.markdown("<div class='footer'>Built for the ROOMAN AI CHALLENGE — Junior AI Research Associate 24-Hour AI Agent Challenge</div>", unsafe_allow_html=True)
