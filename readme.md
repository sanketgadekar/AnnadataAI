
 Run FastAPI server:

uvicorn api.main:app --reload


 Run Streamlit app:

streamlit run app/streamlit_app.py


git pull --rebase origin main
git status
git add .
git commit -m "Describe your change"
git push


python -m src.disease_prediction.train
python -m src.disease_prediction.evaluate
python -m src.disease_prediction.predict