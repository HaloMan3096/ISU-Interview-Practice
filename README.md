# Interview Practice

This repository contains the Interview Practice portion of the Job Tools project.

## Getting Started

### 1. Clone the Repository

If you haven't downloaded the repository yet, open a terminal and run:

```bash
git clone https://github.com/USERNAME/REPOSITORY-NAME.git
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

