▶️ How to run everything
# 1️⃣ Train
python -m src.recommendation.train_model

# 2️⃣ Evaluate
python -m src.recommendation.evaluate_model

# 3️⃣ Predict (single sample)
python -m src.recommendation.predict


✅ Run FastAPI server:

uvicorn api.main:app --reload


✅ Run Streamlit app:

streamlit run app/streamlit_app.py


git status
git add .
git commit -m "Describe your change"
git push
