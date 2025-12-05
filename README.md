# Instructions for running the web app

  🚀 How to Run

  Backend:
  cd lab_5/web_app/backend
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  cp .env.example .env
  # Edit .env with your credentials
  gcloud auth application-default login
  python run.py

  Frontend (in a new terminal):
  cd lab_5/web_app/frontend
  python -m http.server 8080

  Then open http://localhost:8080 in your browser!

# NOTE
all API keys have been deleted in GCP, theese are no longer live and should not have been commited in the first place.
