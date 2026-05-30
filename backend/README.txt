How to run the backend:

1. Open a terminal in the `backend` folder.
2. Activate the Python virtual environment if you have one, for example:
   - `source venv/bin/activate`
3. Install dependencies if needed:
   - `pip install -r requirements.txt`
4. Start the FastAPI app using uvicorn:
   - `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`

If you use ngrok, start the local app first and then run the ngrok helper script:
   - `NGROK_PORT=8000 ./ngrok.sh`