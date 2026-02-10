import streamlit as st
import requests
from app.core.config import API_BASE, DISEASE_ENDPOINT

st.markdown(
    """
    <style>
    /* Change button text & background */
    .stButton > button {
        background-color: #14532d !important;   /* green background */
        color: #ffffff !important;              /* text color */
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
    }

    .stButton > button:hover {
        background-color: #166534 !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def render():
    # ---------------------------------------
    # Page-specific CSS (TEXT COLOR CONTROL)
    # ---------------------------------------
    st.markdown(
        """
        <style>
        /* FORCE ALL TEXT WHITE ON THIS PAGE */
        .stMarkdown,
        .stText,
        .stMarkdown p,
        .stMarkdown span,
        .stMarkdown li,
        label,
        section[data-testid="stFileUploader"] * {
            color: #ffffff !important;
        }

        /* EXCEPTIONS */
        h1, h2 {
            color: #14532d !important;   /* Header stays green */
        }

        /* Image caption */
        figcaption {
            color: #000000 !important;   /* Uploaded Leaf Image */
        }

        /* File uploader container */
        section[data-testid="stFileUploader"] {
            background-color: #1f2933;
            padding: 1.2rem;
            border-radius: 12px;
            border: 1px solid #374151;
        }

        /* Predict button */
        .stButton > button {
            background-color: #14532d !important;
            color: #ffffff !important;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            margin-top: 1rem;
        }

        .stButton > button:hover {
            background-color: #166534 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    # ---------------------------------------
    # Page Content
    # ---------------------------------------
    st.header("🦠 Plant Disease Detection")

    uploaded_file = st.file_uploader(
        "Upload leaf image",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear image of a plant leaf"
    )

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Leaf Image", use_container_width=True)

    if uploaded_file and st.button("Predict Disease"):
        files = {
            "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
        }

        with st.spinner("Analyzing leaf image... 🌿"):
            resp = requests.post(API_BASE + DISEASE_ENDPOINT, files=files)

        if resp.status_code == 200:
            data = resp.json()

            st.success(f"🧪 Detected Disease: **{data['disease']}**")
            st.metric("Confidence", f"{data['confidence']*100:.2f}%")
        else:
            st.error("❌ Failed to analyze image. Please try again.")
