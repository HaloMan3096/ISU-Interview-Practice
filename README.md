# Interview Practice Coach

> **Produced by Claude (Anthropic).** This project was written by **Claude Sonnet 5.5** At run time, the questions and feedback come from whichever model *you* configure (Anthropic’s Claude via API key, or a local model through Ollama).

This repository contains the Interview Practice portion of the Job Tools project.

A small app that runs on your own computer. Paste or upload your résumé, enter the job you want, and practise with tailored questions. You get feedback scored with the **STAR method** (Situation, Task, Action, Result).

It is a **coach, not an answer machine**: it never writes your answers, and its feedback may be wrong, so treat it as guidance. It is for practice and preparation only, not for use during a live interview.

**Contents:** [Quick start](#quick-start) · [Settings](#settings-environment-variables) · [Feedback](#feedback) · [Field-specific questions](#field-specific-questions) · [Privacy](#privacy) · [Project layout](#project-layout) · [Running the tests](#running-the-tests) · [Known limitations](#known-limitations) · [Contributing](#contributing-team-workflow) · [References](#references)

## Quick start

You need **Python 3.9 or newer**. There is nothing to install for the basics.

```bash
git clone https://github.com/HaloMan3096/ISU-Interview-Practice.git
cd ISU-Interview-Practice
```

For a full checklist of what to install, with troubleshooting, see **INSTALL.md**.

Then choose **one** way to power the AI:

**Option A: Anthropic API (Claude)**

```bash
# macOS / Linux
export ANTHROPIC_API_KEY="your-key-here"
python3 app.py

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your-key-here"
python app.py
```

**Option B: Free local model with [Ollama](https://ollama.com)**

```bash
ollama pull llama3.1
python3 app.py          # uses Ollama automatically when no API key is set
```

Your browser opens at http://localhost:8765. With no provider set up, the app still works with generic questions and a STAR self-check.

## Settings (environment variables)

| Variable | Default | Purpose |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | none | Your Anthropic API key. Never stored by the app. |
| `INTERVIEW_PROVIDER` | `anthropic` if a key is set, else `ollama` | `anthropic` or `ollama` |
| `INTERVIEW_MODEL` | `claude-sonnet-5-5` / `llama3.1` | Model name for the chosen provider |
| `OLLAMA_HOST` | `http://localhost:11434` | Where Ollama is running |
| `PORT` | `8765` | Local port |
| `INTERVIEW_REDACT` | `on` | Set to `off` to stop removing personal info before text goes to the AI |
| `REDACT_TERMS` | none | Extra words to always remove, comma-separated, e.g. `Springfield High School,Acme Corp` |

Résumé files: `.txt`, `.md` and `.docx` work out of the box. For `.pdf`, run `pip install pypdf` once. You can always paste text instead.

## Feedback

- **After each answer:** STAR scores (1–5) for Situation, Task, Action and Result, what worked, what to improve, and a reflective question.
- **After the session:** click **Finish session** to see average scores, a recap of every question, and an **overall review** that looks for patterns across all your answers, with priorities and next practice steps. If the overall review fails (for example, the model times out), a **Try again** button appears and your per-question results stay on screen.

## Field-specific questions

The job title drives the questions. Enter something like “Graphic Design”, “IT Support”, “Computer Science” or “Aviation”, pick an experience level, and the AI writes questions a real interviewer in that field would ask (real tools, standards and workflows, not generic ones). More specific titles give sharper questions, e.g. “Junior UX Designer” or “Aircraft Maintenance Technician”.

Without an AI provider, the app falls back to a built-in set of five questions for each of these areas, matched by keywords in the job title: education (teachers, aides), ESL, library, medical and healthcare, animal care and veterinary, graphic design, IT, computer science, aviation, sciences, history, retail and customer service, and food service. Other titles get general behavioral questions. To add a field, add an entry to the `FIELDS` list in `static/index.html`.

## Privacy

- The server listens only on your own machine (`127.0.0.1`).
- Your résumé and answers are sent **only** to the provider you chose: Anthropic’s API, or your local Ollama (which stays on your computer).
- **Personal info is removed on your computer before anything is sent to the AI.** Emails, phone numbers, links (LinkedIn, GitHub, etc.), street addresses, city/state/ZIP, SSN-style numbers, birth dates and the candidate’s name (guessed from the top of the résumé, then also removed from your typed answers) become placeholders like `[EMAIL]` or `[NAME]`. The name is remembered in memory only while the app runs.
- **You can see exactly what is sent.** Under the résumé box the page shows a count of what was removed and the cleaned text with the placeholders highlighted. After each answer it does the same for that answer. The same check is available as `POST /api/redact` (JSON `{"text": "..."}` with the header `X-Requested-With: interview-coach`).
- **This is pattern matching, not a guarantee.** It does not catch employer or school names, unusual name layouts, or personal details written in free text. List those in `REDACT_TERMS`, and read the preview before you start. Do not rely on it for highly sensitive data; for that, use Ollama so nothing leaves your computer.
- The app does not save résumés or answers. The browser keeps only job title and average score for past sessions, and you can clear it with the **Clear** button.
- API usage may cost money on your Anthropic account. Ollama is free but needs a reasonably capable computer.

## Project layout

```
app.py            Local server, prompts, personal-info removal, résumé reading, AI calls (standard library only)
static/index.html The interface
tests/test_app.py Automated tests (standard library only)
INSTALL.md        What to install, with troubleshooting
requirements.txt  Optional: pypdf, for PDF résumés
```

## Running the tests

From the project folder (no extra installs, and no real AI is called):

```bash
python3 -m unittest discover -s tests -v     # Windows: python -m unittest discover -s tests -v
```

The tests cover the personal-info removal (what it must remove and what it must leave alone), the exact prompts that would be sent to the AI, the server’s safety checks, and error messages. Every test has a comment above it explaining what it checks. When you find text that is wrongly removed or wrongly kept, add it as a test first, then fix `app.py`. Tests marked “expected failure” document known limitations.

## Known limitations

- Scoring has not been tested against real interview answers, and AI feedback can be inconsistent. Smaller local models can be generous with scores.
- Personal-info removal is pattern matching (see Privacy). A two-word job title on the first line of a résumé, such as “Software Engineer”, can be mistaken for the candidate’s name; there is an expected-failure test for this.
- Typed answers only (no voice yet); one session at a time.
- Add a license file before sharing publicly (for example MIT) so others know how they may use the code.

## Contributing (team workflow)

Work on your own branch and merge through a pull request; do not push directly to `main`.

### 1. Get the code

If you haven’t cloned the repository yet, see [Quick start](#quick-start). Then make sure your local `main` is up to date:

```bash
git switch main
git pull origin main
```

### 2. Create your own branch

```bash
git switch -c feature/your-name-description
```

For example: `git switch -c feature/alex-resume-upload`

**Branch naming conventions:**
- `feature/` – Adding a new feature.
- `bugfix/` – Fixing an existing issue.
- `docs/` – Updating documentation.
- `test/` – Adding or modifying tests.

### 3. Make and commit your changes

Run the tests before you commit (see [Running the tests](#running-the-tests)). Then check which files changed, stage them, and commit with a descriptive message:

```bash
git status
git add .
git commit -m "Add resume upload functionality"
```

### 4. Push your branch to GitHub

```bash
git push -u origin feature/your-name-description
```

The `-u` option links your local branch to the remote branch, so later pushes can simply use `git push`.

### 5. Pull updates

To get the latest changes from your own remote branch (for example, if you work on more than one computer):

```bash
git pull
```

To bring the latest `main` into your branch:

```bash
git fetch origin
git merge origin/main
```

Resolve any merge conflicts if they occur, then commit the resolution.

### 6. Create a pull request

1. Open the repository on GitHub and go to the **Pull Requests** tab.
2. Select **New Pull Request**.
3. Set the base branch to `main` and the compare branch to your feature branch.
4. Review your changes and create the pull request.
5. Have another team member review the changes before merging.

### Guidelines

- Do not push directly to `main`.
- Create a separate branch for each feature or task.
- Pull the latest changes before starting new work.
- Write descriptive commit messages.
- Push your changes regularly so they are backed up on GitHub.
- Use pull requests to merge completed work into `main`.
- Communicate with the team before making large changes that could affect other features.

### Quick reference

| Task | Command |
|---|---|
| Update main | `git pull origin main` |
| Create a branch | `git switch -c branch-name` |
| Switch branches | `git switch branch-name` |
| Check changes | `git status` |
| Stage changes | `git add .` |
| Commit changes | `git commit -m "Message"` |
| Push changes | `git push` |
| Get latest branch changes | `git pull` |
| Get remote updates | `git fetch origin` |
| Merge latest main | `git merge origin/main` |

## References

1. Business case “Business Case: AI Interview Prep. System”, ECT 437-301 Industrial Computer Systems Management (project team including Jennafer Ortiz; sponsor Jeff Kinne), file `Business_Case_Interview__.docx`. Source of the requirements: résumé-based questions, STAR evaluation, practice not answers, an AI-may-be-wrong notice, and no résumé storage unless requested.
2. The STAR method (Situation, Task, Action, Result), a widely used behavioral-interview framework. From Claude’s training data; no specific web page was consulted.
3. Anthropic Messages API and Ollama chat API request formats, and Python standard-library `http.server`, `urllib`, `zipfile`, `unittest`. From Claude’s training data; no online documentation was retrieved while writing this.
4. General interview-coaching practice and common behavioral and technical question styles, from Claude’s training data.
5. The personal-info patterns (emails, phones, addresses, and so on) were written for this project and tested on sample résumés; they are not taken from a published standard.