# AZN-Intelligence

## Project Overview

AZN-Intelligence is a web accessibility grader agent built with ConnectOnion. It analyzes the accessibility of webpages (using WCAG criteria) and re-ranks search results to prioritize accessible sites. The agent uses AI to check the scraped HTML and CSS, assigns a grade (A, AA, AAA), and stores results in a JSON file.

### Key Features
- Scrapes webpage HTML for analysis
- AI-powered accessibility grading (no screenshots required)
- Grades based on WCAG (A, AA, AAA)
- Summarizes accessibility issues
- Re-ranks search results by accessibility
- Persists results in `results.json`

---

## Quick Setup Guide (For Teammates)

Follow these steps to set up the project on your computer:

### 1. Clone the Repository
```sh
git clone https://github.com/Thambolo/AZN-Intelligence.git
cd AZN-Intelligence/meta-agent
```

### 2. Create and Activate a Python Virtual Environment
```sh
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
# If requirements.txt is missing, install manually:
pip install connectonion beautifulsoup4 requests python-dotenv
```

### 4. Set Up Environment Variables
- Copy `.env.example` to `.env` (if not already present)
- Add your OpenAI API key to `.env`:
	```env
	OPENAI_API_KEY=sk-...
	```

### 5. Run the Agent
```sh
python agent.py
```
- The agent will analyze example URLs and save results to `results.json`.

### 6. Troubleshooting
- If you see `ModuleNotFoundError`, install the missing package with `pip install <package>`.
- If you see an OpenAI API key error, make sure your `.env` is set up and loaded (see code for `python-dotenv` usage).

---

## Customization
- Edit `agent.py` to change the URLs or add new features.
- The system prompt is in `prompts/accessibility_grader.md` for easy editing.

---

## Useful Commands
- Activate venv: `.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (macOS/Linux)
- Install dependencies: `pip install -r requirements.txt`
- Run agent: `python agent.py`

---

## License
MIT