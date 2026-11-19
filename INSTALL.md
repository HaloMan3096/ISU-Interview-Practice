# Interview Practice Coach: What You Need to Install

> **Produced by Claude (Anthropic).** Written by **Claude Sonnet 5.5** in **Jennafer Ortiz’s Claude account**. Prompt: Jennafer asked for an updated download of the Interview Practice Coach together with a document listing what must be installed for it to run, following our discussion of setup in this conversation.

*Testing note: Claude tested the server code with fake AI replies only. It has not been tested on Windows or against a real AI model, and computers differ, so treat these steps as a guide.*

## Quick checklist

- **Python 3.9 or newer** (required)
- **A web browser** such as Chrome (required)
- **The project folder from the zip, fully extracted** (required)
- **One AI option** (recommended): Ollama with the `llama3.1` model (free, runs on your computer) **or** an Anthropic API key (paid per use). With neither, the app still runs but only gives built-in questions and a STAR self-check.
- **pypdf** (optional): only if you want to upload PDF résumés

## Step 1: Install Python

1. Check whether you have it: run `python3 --version` (Windows: `python --version`). You need 3.9 or newer.
2. If it’s missing, download it from python.org. On Windows, tick **Add Python to PATH** in the installer.

## Step 2: Extract the project

Extract the zip fully (Windows: right-click, then Extract All; don’t run it from inside the zip). The folder should contain `app.py`, `README.md`, `INSTALL.md`, `requirements.txt` and a `static` folder holding `index.html`.

## Step 3: Choose how the AI runs

**Option A: Ollama (free, runs on your computer)**

1. Install Ollama from ollama.com and open it.
2. In a terminal run `ollama pull llama3.1`. It’s a download of about 5 GB, so leave the window open until it says success.
3. Run `ollama list`. `llama3.1` should appear.
4. On an older or slow laptop, a smaller model is faster: `ollama pull llama3.2`, then start the app with `INTERVIEW_MODEL=llama3.2` set. Feedback from smaller models is rougher.

**Option B: Claude through the Anthropic API (paid per use)**

1. Create an account and an API key in Anthropic’s developer console, and set up billing. Check current pricing there.
2. In the same terminal where you will start the app, set the key:
   - Mac or Linux: `export ANTHROPIC_API_KEY="your-key"`
   - Windows PowerShell: `$env:ANTHROPIC_API_KEY="your-key"`
3. Keep the key private. Don’t share it or put it on GitHub.

**Option C: No AI.** The app still works with built-in questions and a STAR self-check.

## Step 4 (optional): PDF résumés

Run `python3 -m pip install pypdf` once (Windows: `python -m pip install pypdf`). Or run `python3 -m pip install -r requirements.txt`. Scanned PDFs without selectable text can’t be read, so paste the text instead.

If a Mac shows “externally-managed-environment”, use a virtual environment: run `python3 -m venv .venv`, then `source .venv/bin/activate`, then `pip install pypdf`. Run the activate line again in every new terminal window.

## Step 5: Start the app

1. Open a terminal in the project folder.
2. Run `python3 app.py` (Windows: `python app.py`).
3. Leave that window open. The app opens at http://localhost:8765. Stop it with Ctrl+C.

## Check that it’s working

The terminal prints a line when the app starts, and the page shows the same information at the top.
- `provider: ollama, model: llama3.1` means Ollama is selected.
- `provider: anthropic, model: claude-sonnet-5-5` means Claude is selected.

The app picks Claude if an API key is set, and otherwise Ollama. The line shows what is selected, not whether it is working.

## Common problems

- **“This page isn’t working” or “Can’t reach the local server”:** `app.py` isn’t running, or `index.html` was opened directly (the address starts with `file://`). Start the app and use http://localhost:8765.
- **“Couldn’t reach Ollama”:** open the Ollama app, then check that http://localhost:11434 says “Ollama is running”.
- **“Ollama doesn’t have the model”:** run `ollama pull llama3.1`.
- **`command not found: ollama`:** Ollama isn’t installed, or the terminal needs reopening after installing.
- **Very slow answers or timeouts:** try a smaller model, or use the Claude API option.
- **PDF message:** follow Step 4.
- **Port already in use:** start with a different port, for example `PORT=8800 python3 app.py` (PowerShell: `$env:PORT="8800"` first).

## For group testing

Agree on one setup so results are comparable, and confirm everyone’s startup line matches. Résumés and answers go to whichever AI you chose: with Ollama they stay on your computer, and with the Claude API they are sent to Anthropic.

## References

1. Business case “Business Case: AI Interview Prep. System”, ECT 437-301 Industrial Computer Systems Management (project team including Jennafer Ortiz; sponsor Jeff Kinne), file `Business_Case_Interview__.docx`.
2. The project files in this download (`app.py`, `static/index.html`, `README.md`) and the testing described in this conversation.
3. Setup details for Python, Ollama and the Anthropic API come from Claude’s training data. No online documentation was retrieved, so confirm current steps and pricing at python.org, ollama.com and Anthropic’s developer documentation.
