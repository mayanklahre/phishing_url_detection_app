# Phishing URL Detection 

This is a small, ready-to-open project you can use in VS Code for your college demo.
It contains:
- `main.py` — command-line script demonstrating predictions.
- `predict.py` — a small heuristic-based URL "detector" (no heavy ML libraries).
- `app.py` — minimal Flask web GUI (open at http://127.0.0.1:5000).
- `requirements.txt` — minimal Python packages.
- `templates/index.html`, `static/style.css` — UI files.
- `.vscode/launch.json` — quick run/debug configs.
- `PROGRESS.md` — demo progress notes.

**Why heuristic-based?**
This implementation uses deterministic URL heuristics (length, IP in domain, suspicious tokens)
so it is lightweight, runs without downloading heavy ML packages (like pycaret), and works offline.
For the real project you can replace `predict()` in `predict.py` with your trained model.

## How to open in VS Code
1. Download the zip `phishing_url_detection_app.zip` from the link below.
2. Unzip and open the folder in VS Code.
3. Create & activate a virtual environment:
   - Windows PowerShell:
     ```
     python -m venv zenv
     .\zenv\Scripts\Activate.ps1
     ```
   - macOS/Linux:
     ```
     python3 -m venv zenv
     source zenv/bin/activate
     ```
4. Install requirements:
   ```
   pip install -r requirements.txt
   ```
5. Run CLI demo:
   ```
   python main.py
   ```
6. Run web GUI:
   ```
   python app.py
   ```
   Open http://127.0.0.1:5000

## Notes for your demo
- This is a functional demo suitable for college presentation.
- Replace `/ test URLs /` in `main.py` with URLs you want to test.
- To integrate ML later, replace `predict()` implementation in `predict.py`.
