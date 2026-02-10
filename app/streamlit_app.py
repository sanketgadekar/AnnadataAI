import streamlit as st
import sys
from pathlib import Path
st.markdown(
    """
    <style>
    /* GLOBAL BUTTON STYLE */
    .stButton > button {
        background-color: #52a447 !important;   /* main button color */
        color: #ffffff !important;              /* text color */
        border-radius: 8px;
        padding: 0.6rem 1.3rem;
        font-weight: 600;
        border: none;
    }

    /* Hover effect */
    .stButton > button:hover {
        background-color: #46963e !important;   /* slightly darker green */
        color: #ffffff !important;
    }

    /* Disabled button */
    .stButton > button:disabled {
        background-color: #9ccf97 !important;
        color: #ffffff !important;
        opacity: 0.7;
        cursor: not-allowed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# GLOBAL THEME (Background + Text)
# ============================================================
st.markdown(
    """
    <style>
    /* App background */
    .stApp {
        background-color: #F9FAF7;
    }

    /* FORCE ALL TEXT TO PURE BLACK */
    html, body,
    p, span, li, label,
    .stMarkdown, .stText,
    section[data-testid="stSidebar"] * {
        color: #000000 !important;
    }

    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background-color: #EEF1EC !important;
        padding: 1.2rem;
    }

    /* HEADER / TITLE COLORS (EXPLICITLY ALLOWED) */
    h1, h2, h3 {
        color: #14532d !important;
    }

    /* Sidebar title (allowed to be green) */
    .sidebar-title {
        font-size: 22px;
        font-weight: 700;
        color: #14532d !important;
        margin-bottom: 0.25rem;
    }

    /* Sidebar subtitle — NOW BLACK */
    .sidebar-subtitle {
        font-size: 13px;
        margin-bottom: 1rem;
        color: #000000 !important;
    }

    /* Sidebar radio spacing */
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 0.6rem;
    }

    section[data-testid="stSidebar"] label {
        font-size: 15px;
        font-weight: 500;
        color: #000000 !important;
    }

    /* Profile section — NOW BLACK */
    .sidebar-profile {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #d1d5db;
        font-size: 13px;
        color: #000000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# PATH FIX (DO NOT TOUCH)
# ============================================================
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ============================================================
# IMPORT VIEWS (UNCHANGED)
# ============================================================
from app.views import (
    home, crop, fertilizer, yield_, irrigation, soil_health, disease, about
)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="AnnadataAI", layout="wide")

# ============================================================
# SESSION STATE
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "Home"

# ============================================================
# SIDEBAR (REDESIGNED)
# ============================================================
with st.sidebar:
    # App branding
    st.markdown("<div class='sidebar-title'>AnnadataAI 🌾</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sidebar-subtitle'>AI-Powered Smart Agriculture</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # Navigation
    pages = [
        "🏠 Home",
        "🌱 Crop Recommendation",
        "🧪 Fertilizer Recommendation",
        "📈 Yield Prediction",
        "🦠 Disease Detection",
        "🚰 Irrigation Scheduler",
        "🧬 Soil Health Check",
        "ℹ️ About",
    ]

    page_map = {
        "🏠 Home": "Home",
        "🌱 Crop Recommendation": "Crop Recommendation",
        "🧪 Fertilizer Recommendation": "Fertilizer Recommendation",
        "📈 Yield Prediction": "Yield Prediction",
        "🦠 Disease Detection": "Disease Detection",
        "🚰 Irrigation Scheduler": "Irrigation Scheduler",
        "🧬 Soil Health Check": "Soil Health Check",
        "ℹ️ About": "About",
    }

    selected = st.radio(
        "Navigation",
        pages,
        index=list(page_map.values()).index(st.session_state.page),
        label_visibility="collapsed"
    )

    st.session_state.page = page_map[selected]

    st.divider()

    # User / Project info
    st.markdown(
        """
        <div class="sidebar-profile">
        <strong>👤 Developer</strong><br>
        Sanket Gadekar<br><br>
        <strong>🎓 Project</strong><br>
        College Academic Project
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# ROUTING (UNCHANGED)
# ============================================================
page = st.session_state.page

if page == "Home":
    home.render()
elif page == "Crop Recommendation":
    crop.render()
elif page == "Fertilizer Recommendation":
    fertilizer.render()
elif page == "Yield Prediction":
    yield_.render()
elif page == "Disease Detection":
    disease.render()
elif page == "Irrigation Scheduler":
    irrigation.render()
elif page == "Soil Health Check":
    soil_health.render()
elif page == "About":
    about.render()
