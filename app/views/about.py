import streamlit as st


def render():
    st.header("🌾 About AnnadataAI")

    st.markdown(
        """
        **AnnadataAI** is an AI-powered smart agriculture platform developed as a
        **college academic project**, aimed at helping farmers make
        **data-driven decisions** across the farming lifecycle.

        This project integrates **machine learning, environmental data,
        and agricultural insights** to improve crop productivity,
        optimize resource usage, and reduce farming risks.
        """
    )

    st.markdown("---")

    st.subheader("🚜 Key Features")

    st.markdown(
        """
        - 🌱 **Crop Recommendation** based on soil nutrients, pH, and climate
        - 🧪 **Fertilizer Recommendation** using soil and crop information
        - 📈 **Yield Prediction** using historical agricultural and climate data
        - 🦠 **Plant Disease Detection** from leaf images using deep learning
        - 🚰 **Irrigation Scheduling** based on soil moisture and weather conditions
        - 🧬 **Soil Health Analysis** using nutrient composition and pH values
        """
    )

    st.markdown("---")

    st.subheader("🧠 Technologies Used")

    st.markdown(
        """
        - Python, Machine Learning, and Deep Learning  
        - FastAPI for backend model deployment  
        - Streamlit for interactive user interface  
        - Public agricultural and plant disease datasets  
        """
    )

    st.markdown("---")

    st.subheader("🎓 Academic Context")

    st.markdown(
        """
        This project is developed as part of an academic curriculum to demonstrate
        practical applications of **Artificial Intelligence in Agriculture**,
        focusing on real-world problem solving and system design.
        """
    )

    st.markdown("---")

    st.subheader("👨‍💻 Developed By")

    st.markdown(
        """
        **Sanket Gadekar**  
        Undergraduate Student – Artificial Intelligence 
     
        """
    )

    st.caption(
        "AnnadataAI — Leveraging AI to support sustainable and smart farming 🌱"
    )
