import streamlit as st
st.markdown(
    """
    <style>
    /* Sticky header wrapper */
    .sticky-header {
        position: sticky;
        top: 0;
        background-color: #F9FAF7;
        z-index: 999;
        padding-top: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }

    /* Remove default margin jump */
    .sticky-header h1 {
        margin-bottom: 0.2rem;
    }

    .sticky-header h4 {
        margin-top: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def render():
    # --------------------------
    # Page Background (Plain Color)
    # --------------------------
    st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background-color: #F9FAF7;
    }

    /* Force ALL normal text to black */
    .stMarkdown,
    .stText,
    .stMarkdown p,
    .stMarkdown span,
    .stMarkdown li,
    .stMarkdown div {
        color: #000000 !important;
    }

    /* Optional: center content nicely */
    .block-container {
        padding-top: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


    # --------------------------
    # Start content card
    # --------------------------
    st.markdown("<div class='home-card'>", unsafe_allow_html=True)

    # --------------------------
    # Title & Subtitle
    # --------------------------
    st.markdown(
        """
        <div class="sticky-header">
            <h1 style="color:#14532d; text-align:center;">
                Welcome to AnnadataAI 🌾
            </h1>
            <h4 style="text-align:center; color:#000000;">
                AI-Powered Smart Agriculture Assistant
            </h4>
            <hr/>
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown("---")

    # --------------------------
    # Introduction
    # --------------------------
    st.markdown(
        """
        <p>
        <strong>AnnadataAI</strong> is an AI-powered smart agriculture platform developed as a  
        <strong>college academic project</strong>, designed to help farmers make informed decisions
        using <strong>Artificial Intelligence and data analytics</strong>.
        </p>

        <p>
        The system integrates soil data, climate information, and machine learning
        models to deliver <strong>practical, easy-to-understand recommendations</strong>
        for sustainable farming.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # --------------------------
    # Features
    # --------------------------
    st.subheader("🌱 What You Can Do with AnnadataAI")

    st.markdown(
        """
        <ul>
            <li>🌾 <strong>Crop Recommendation</strong> – Best crops for your soil & climate</li>
            <li>🧪 <strong>Fertilizer Recommendation</strong> – Right nutrients for better yield</li>
            <li>📈 <strong>Yield Prediction</strong> – Estimate crop production in advance</li>
            <li>🦠 <strong>Disease Detection</strong> – Identify plant diseases from leaf images</li>
            <li>🚰 <strong>Irrigation Scheduling</strong> – Smart water usage decisions</li>
            <li>🧬 <strong>Soil Health Check</strong> – Overall soil condition analysis</li>
        </ul>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # --------------------------
    # Call to Action
    # --------------------------
    st.success("👉 Use the **sidebar menu** to explore AnnadataAI features.")

    st.caption(
        "Developed by Sanket Gadekar | AnnadataAI 🌱"
    )

    # --------------------------
    # End content card
    # --------------------------
    st.markdown("</div>", unsafe_allow_html=True)
