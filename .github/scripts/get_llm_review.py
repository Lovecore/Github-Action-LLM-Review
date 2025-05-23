# .github/scripts/get_llm_review.py
import os
import sys
import json
from openai import OpenAI

def get_llm_review(code_file_path, output_file_path):
    """
    Sends a full Python code file to an LLM for review and saves the review.
    """
    review_content = "No review generated."
    try:
        # Get secrets/env vars in a robust way for GitHub Actions
        api_key = os.environ.get('LLM_API_KEY')
        llm_endpoint = os.environ.get('LLM_ENDPOINT')
        model_name = os.environ.get('LLM_MODEL_NAME')

        missing_vars = []
        if not api_key:
            missing_vars.append('LLM_API_KEY')
        if not llm_endpoint or llm_endpoint == "YOUR_LLM_API_ENDPOINT_HERE":
            missing_vars.append('LLM_ENDPOINT')
        if not model_name or model_name == "YOUR_LLM_MODEL_NAME_HERE":
            missing_vars.append('LLM_MODEL_NAME')

        if missing_vars:
            review_content = (
                f"Error: The following required environment variables are missing or not set properly: {', '.join(missing_vars)}.\n"
                f"Current values:\n"
                f"  LLM_API_KEY: {'set' if api_key else 'NOT SET'}\n"
                f"  LLM_ENDPOINT: {llm_endpoint or 'NOT SET'}\n"
                f"  LLM_MODEL_NAME: {model_name or 'NOT SET'}\n\n"
                "In your GitHub workflow, set these with:")
            review_content += '''\n
      env:
        LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
        LLM_ENDPOINT: ${{ secrets.LLM_ENDPOINT }}
        LLM_MODEL_NAME: ${{ secrets.LLM_MODEL_NAME }}
'''
            print(review_content)
            with open(output_file_path, 'w') as outfile:
                outfile.write(review_content)
            sys.exit(1)

        with open(code_file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()

        if not code_content.strip():
            print("No code detected in the file. Skipping LLM review.")
            review_content = "No code detected to review."
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                outfile.write(review_content)
            return

        # IMPORTANT: Customize this prompt for your needs and your specific LLM.
        prompt = f"""You are an expert AI code reviewer.
Please perform a security and design review of the following Python code file.
Focus on:
1.  **Security Vulnerabilities**: Identify potential issues like injection flaws, XSS, CSRF, insecure data handling, hardcoded secrets, authentication/authorization bypasses, etc.
2.  **Design Flaws**: Look for anti-patterns, code smells, poor readability, lack of modularity, performance bottlenecks, and deviations from best practices.
3.  **Maintainability & Scalability**: Assess if the code is easy to understand, maintain, and scale.

Provide clear, concise, and actionable feedback. If possible, suggest improvements or alternatives.
If no significant issues are found, please state that.

```python
{code_content}
```

Review:
"""

        # --- LLM API Call (NEEDS HEAVY CUSTOMIZATION) ---
        # This section is HIGHLY DEPENDENT on the LLM API you are using.
        # You MUST adapt the headers, payload, and response parsing to your specific LLM.

        # Use OpenAI v1+ python library interface
        try:
            client = OpenAI(api_key=api_key)
            # Optionally set api_base if using a custom endpoint
            if llm_endpoint and llm_endpoint != "https://api.openai.com/v1/chat/completions":
                client.base_url = llm_endpoint.rstrip("/chat/completions")
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=0.3,
            )
            review_text = response.choices[0].message.content
        except Exception as e:
            review_text = f"Error calling OpenAI API: {type(e).__name__}: {e}"

        review_content = review_text.strip()
        print(review_content)
    except requests.exceptions.RequestException as req_err:
        review_content = f"Error calling LLM API (RequestException): {req_err}"
        print(review_content)
    except KeyError as key_err:  # Should be caught by earlier checks, but as a safeguard
        review_content = (
            f"Error: Missing critical environment variable: {key_err}. "
            "Please ensure all required variables (LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL_NAME) are set."
        )
        print(review_content)
    except Exception as e:
        review_content = (
            f"An unexpected error occurred in the LLM script: {type(e).__name__} - {e}"
        )
        print(review_content)
    finally:
        # Ensure output directory exists (only if directory is not empty)
        output_dir = os.path.dirname(output_file_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Always write the result (either the review or error message) to the output file
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            outfile.write(review_content)

        if "Error:" in review_content:
            print(f"LLM review script finished with errors. Output written to {output_file_path}")
            return 1
        else:
            print(f"Review successfully generated and written to {output_file_path}")
            return 0

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python get_llm_review.py <code_file_path> <output_file_path>")
        sys.exit(1)
    code_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    sys.exit(get_llm_review(code_file_path, output_file_path))
