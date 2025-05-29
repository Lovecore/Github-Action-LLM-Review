# LLM Code Review GitHub Action

A GitHub Action that automatically performs AI-powered code reviews on Pull Requests using Large Language Models (LLMs).

## Overview

This repository contains a GitHub Action that automatically analyzes Python code changes in pull requests and generates detailed code reviews using an LLM. The action identifies security vulnerabilities, design flaws, and suggests improvements to help maintain code quality and security standards.

## Features

- **Automated Code Reviews**: Automatically runs on every pull request to selected branches
- **Security Focus**: Identifies potential security vulnerabilities in code changes
- **Design Analysis**: Highlights design flaws, anti-patterns, and code smells
- **Structured Output**: Provides a clear table of issues with risk levels and recommendations
- **Customizable**: Configurable to work with different LLM providers and models

## Setup

### 1. Repository Configuration

Add this GitHub Action to your repository by creating the following workflow file:

```yaml
# .github/workflows/llm-review.yml
name: LLM Code Review

on:
  pull_request:
    branches: [ main, master ] # Adjust to your main branch name

permissions:
  contents: read # Allows checkout of the repository

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Fetches all history to allow diffing against base branch

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: pip install -r requirements.txt

      - name: Generate Diff
        id: git_diff
        run: |
          git fetch origin ${{ github.event.pull_request.base.ref }} --depth=1
          git diff --no-prefix "origin/${{ github.event.pull_request.base.ref }}" ${{ github.sha }} > changes.diff
          echo "diff_file=changes.diff" >> $GITHUB_OUTPUT

      - name: Analyze Changed Python Files
        id: analyze_py_files
        run: |
          git diff --name-only ${{ github.event.pull_request.base.sha }} ${{ github.sha }} | grep '\.py$' > changed_py_files.txt || true
          if [ ! -s changed_py_files.txt ]; then
            echo "No Python files changed. Skipping analysis."
            exit 0
          fi
          while IFS= read -r file; do
            echo "Analyzing $file..."
            safe_file_name=$(echo "$file" | tr '/' '_')
            python .github/scripts/get_llm_review.py "$file" "llm_review_${safe_file_name}.md"
          done < changed_py_files.txt
        env:
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
          LLM_ENDPOINT: ${{ vars.LLM_ENDPOINT }}
          LLM_MODEL_NAME: ${{ vars.LLM_MODEL_NAME }}

      - name: Upload Review Documents
        if: success() || failure()
        uses: actions/upload-artifact@v4
        with:
          name: llm-code-review-report
          path: llm_review_*.md
```

### 2. Configure Secrets and Variables

In your GitHub repository settings, add the following:

1. **Secrets**:
   - `LLM_API_KEY`: Your API key for the LLM service

2. **Variables**:
   - `LLM_ENDPOINT`: The API endpoint for your LLM provider (e.g., `https://api.openai.com/v1/chat/completions`)
   - `LLM_MODEL_NAME`: The model name to use (e.g., `gpt-4`)

## How It Works

1. When a pull request is opened or updated, the action:
   - Checks out the repository code
   - Generates a diff between the base branch and the PR
   - Identifies changed Python files
   - Sends each changed file to the LLM for review
   - Generates a markdown report for each file
   - Uploads the reports as artifacts

2. The LLM analyzes each file for:
   - Security vulnerabilities
   - Design flaws and anti-patterns
   - Code quality issues
   - Best practice violations

3. The review output includes:
   - Detailed analysis of potential issues
   - Risk assessment for each issue
   - Recommendations for improvements
   - Code snippets highlighting problem areas

## Customization

You can customize the review focus by modifying the prompt in `.github/scripts/get_llm_review.py`. The default prompt focuses on security and design, but you can adjust it to emphasize:

- Performance optimization
- Compliance with specific coding standards
- Test coverage analysis
- Documentation quality
- Or other aspects important to your project

## Requirements

- GitHub repository with Python code
- Access to an LLM API (OpenAI or compatible)
- Python 3.6+ for running the review script