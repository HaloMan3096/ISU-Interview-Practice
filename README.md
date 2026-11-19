# Interview Practice

This repository contains the Interview Practice portion of the Job Tools project.

## Getting Started

### 1. Clone the Repository

If you haven't downloaded the repository yet, open a terminal and run:

```bash
git clone https://github.com/HaloMan3096/ISU-Interview-Practice.git
```

Navigate into the project directory:

```bash
cd REPOSITORY-NAME
```

### 2. Create Your Own Branch

Before making any changes, create a separate branch for your work.

First, make sure your local `main` branch is up to date:

```bash
git switch main
git pull origin main
```

Create a new branch:

```bash
git switch -c feature/your-name-description
```

For example:

```bash
git switch -c feature/alex-resume-upload
```

**Branch naming conventions:**
- `feature/` – Adding a new feature.
- `bugfix/` – Fixing an existing issue.
- `docs/` – Updating documentation.
- `test/` – Adding or modifying tests.

### 3. Make and Commit Your Changes

Make your changes to the project. When you're ready to save your work, check which files have been modified:

```bash
git status
```

Stage your changes:

```bash
git add .
```

Commit your changes with a descriptive message:

```bash
git commit -m "Add resume upload functionality"
```

### 4. Push Your Branch to GitHub

Push your branch to the remote repository:

```bash
git push -u origin feature/your-name-description
```

The `-u` option links your local branch to the remote branch, so future pushes can simply use:

```bash
git push
```

### 5. Pull Updates From Your Branch

If you are working on multiple computers or want to retrieve the latest changes from your own remote branch, run:

```bash
git pull
```

To retrieve the latest changes from the main branch, first fetch the remote updates:

```bash
git fetch origin
```

Then merge the latest `main` branch into your current branch:

```bash
git merge origin/main
```

Resolve any merge conflicts if they occur, then commit the resolution if necessary.

### 6. Create a Pull Request

Once your work is ready to be added to the main project:

1. Open the repository on GitHub.
2. Navigate to the **Pull Requests** tab.
3. Select **New Pull Request**.
4. Set the base branch to `main`.
5. Set the compare branch to your feature branch.
6. Review your changes and create the pull request.
7. Have another team member review the changes before merging.

## Important Guidelines

- **Do not push directly to `main`.**
- Create a separate branch for each feature or task.
- Pull the latest changes before starting new work.
- Write descriptive commit messages.
- Push your changes regularly so they are backed up on GitHub.
- Use pull requests to merge completed work into `main`.
- Communicate with the team before making large changes that could affect other features.

## Quick Reference

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

# Interview Practice Coach

> **Produced by Claude (Anthropic).** This project was written by **Claude Sonnet 5.5** in **Jennafer Ortiz’s Claude account**. Prompts used: Jennafer asked for an app that helps users practise for job interviews and shared the ECT 437 business case “AI Interview Prep. System”; she then asked for a version that can be shared on GitHub and run on a person’s own computer. At run time, the questions and feedback come from whichever model *you* configure (Anthropic’s Claude via API key, or a local model through Ollama).

A small app that runs on your own computer. Paste or upload your résumé, enter the job you want, and practise with tailored questions. You get feedback scored with the **STAR method** (Situation, Task, Action, Result).

It is a **coach, not an answer machine**: it never writes your answers, and its feedback may be wrong, so treat it as guidance. It is for practice and preparation only, not for use during a live interview.

## Quick start

You need **Python 3.9 or newer**. There is nothing to install for the basics.

```bash
git clone <your-repo-url>
cd interview-practice-coach
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
- The app does not save résumés or answers. The browser keeps only job title and average score for past sessions, and you can clear it with the **Clear** button.
- API usage may cost money on your Anthropic account. Ollama is free but needs a reasonably capable computer.

## Project layout

```
app.py            Local server, prompts, résumé reading, AI calls (standard library only)
static/index.html The interface
```

## Known limitations

- Scoring has not been tested against real interview answers, and AI feedback can be inconsistent.
- Typed answers only (no voice yet); one session at a time.
- Add a license file before sharing publicly (for example MIT) so others know how they may use the code.

## References

1. Business case “Business Case: AI Interview Prep. System”, ECT 437-301 Industrial Computer Systems Management (project team including Jennafer Ortiz; sponsor Jeff Kinne), file `Business_Case_Interview__.docx`. Source of the requirements: résumé-based questions, STAR evaluation, practice not answers, an AI-may-be-wrong notice, and no résumé storage unless requested.
2. The STAR method (Situation, Task, Action, Result), a widely used behavioral-interview framework. From Claude’s training data; no specific web page was consulted.
3. Anthropic Messages API and Ollama chat API request formats, and Python standard-library `http.server`, `urllib`, `zipfile`. From Claude’s training data; no online documentation was retrieved while writing this.
4. General interview-coaching practice and common behavioral and technical question styles, from Claude’s training data.
