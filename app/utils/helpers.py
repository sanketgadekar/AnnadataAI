import streamlit as st

def mock_top3(ph):
    if ph < 5.8:
        top = [("Paddy", 0.62), ("Maize", 0.25), ("Millet", 0.13)]
    else:
        top = [("Maize", 0.58), ("Soybean", 0.27), ("Wheat", 0.15)]
    return {
        "recommended_crop": top[0][0],
        "top3": [{"crop": c, "probability": p} for c, p in top],
        "rationale": f"Mock rationale for pH={ph}",
    }

def display_top3(data):
    recommended = data.get("recommended_crop", "—")
    top3 = data.get("top3", [])
    rationale = data.get("rationale", "")

    st.success(f"✅ Recommended Crop: **{recommended}**")
    if top3:
        for i, entry in enumerate(top3, start=1):
            st.write(
                f"{i}. **{entry.get('crop')}** — {entry.get('probability',0)*100:.1f}%"
            )
    if rationale:
        st.info(rationale)
