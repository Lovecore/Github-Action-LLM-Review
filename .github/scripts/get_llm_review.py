# .github/scripts/get_llm_review.py
import os
import sys
import requests
import json

def get_llm_review(diff_file_path, output_file_path):
    """
    Sends code diff to an LLM for review and saves the review.
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

        with open(diff_file_path, 'r', encoding='utf-8') as f:
            diff_content = f.read()

        if not diff_content.strip():
            print("No code changes detected in the diff. Skipping LLM review.")
            review_content = "No code changes detected to review."
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                outfile.write(review_content)
            return

        # IMPORTANT: Customize this prompt for your needs and your specific LLM.
        prompt = f"""You are an expert AI code reviewer.
Please perform a security and design review of the following code changes, provided in a 'git diff' format.
Focus on:
1.  **Security Vulnerabilities**: Identify potential issues like injection flaws, XSS, CSRF, insecure data handling, hardcoded secrets, authentication/authorization bypasses, etc.
2.  **Design Flaws**: Look for anti-patterns, code smells, poor readability, lack of modularity, performance bottlenecks, and deviations from best practices.
3.  **Maintainability & Scalability**: Assess if the code is easy to understand, maintain, and scale.

Provide clear, concise, and actionable feedback. If possible, suggest improvements or alternatives.
If no significant issues are found, please state that.

```diff
{diff_content}

Review:
""" 
        # --- LLM API Call (NEEDS HEAVY CUSTOMIZATION) ---
        # This section is HIGHLY DEPENDENT on the LLM API you are using.
        # You MUST adapt the headers, payload, and response parsing to your specific LLM.

        headers = {
            "Authorization": f"Bearer {api_key}", # Common for many APIs using Bearer tokens
            "Content-Type": "application/json"
            # Add other headers your LLM might need. For example, Anthropic requires 'x-api-key' and 'anthropic-version'.
            # "anthropic-version": "2024-6-01" # Example for Anthropic
        }

        # This payload structure is a GENERIC EXAMPLE and likely needs to be changed.
        # Consult your LLM provider's API documentation.
        #
        # Example for OpenAI (Chat Completions API):
        # payload = {
        #     "model": model_name,
        #     "messages": [{"role": "user", "content": prompt}],
        #     "max_tokens": 2048,
        #     "temperature": 0.3
        # }
        #
        # Example for Anthropic Claude:
        # payload = {
        #     "model": model_name,
        #     "messages": [{"role": "user", "content": prompt}],
        #     "max_tokens": 2048,
        #     "system": "You are an expert AI code reviewer." # System prompt can sometimes be separate
        # }
        #
        # ADAPT THIS PAYLOAD TO YOUR LLM:
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}], # Common pattern
            # "prompt": prompt, # Some older APIs might use this directly
            "max_tokens": 3000, # Adjust based on expected review length and model limits
            "temperature": 0.2  # Lower temperature for more deterministic, factual reviews
        }

        print(f"Sending request to LLM endpoint: {llm_endpoint} with model: {model_name}")
        # Consider adding a timeout, e.g., timeout=300 (for 5 minutes)
        response = requests.post(llm_endpoint, headers=headers, json=payload, timeout=300)
        response.raise_for_status() # This will raise an HTTPError for bad responses (4XX or 5XX)

    # --- Parse LLM Response (NEEDS HEAVY CUSTOMIZATION) ---
    # This part is also HIGHLY DEPENDENT on your LLM's API response format.
    #
    # Example for OpenAI (Chat Completions API):
    # review_text = response.json()['choices'][0]['message']['content']
    #
    # Example for Anthropic Claude:
    # review_text = response.json()['content'][0]['text']
    #
    # ADAPT THIS PARSING LOGIC:
    try:
        response_data = response.json()
        # Try OpenAI-like structure first
        if 'choices' in response_data and response_data['choices'] and 'message' in response_data['choices'][0] and 'content' in response_data['choices'][0]['message']:
            review_text = response_data['choices'][0]['message']['content']
        # Try Anthropic Claude-like structure
        elif 'content' in response_data and response_data['content'] and 'text' in response_data['content'][0]:
            review_text = response_data['content'][0]['text']
        # Add other parsing logic for different LLMs as needed
        # else:
        # review_text = response_data.get("review", "Error: Could not parse 'review' field from LLM response.") # Generic fallback
        else:
            review_text = f"Error: Could not parse review from LLM response using common patterns. Raw response: \n{json.dumps(response_data, indent=2)}"

    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as parse_error:
        review_text = f"Error parsing LLM JSON response: {parse_error}. \nRaw response text: \n{response.text}"

    review_content = review_text.strip()

except requests.exceptions.Timeout:
    review_content = "Error: The request to the LLM API timed out after 5 minutes."
    print(review_content)
except requests.exceptions.HTTPError as http_err:
    review_content = f"HTTP error occurred: {http_err}\nResponse Content: {http_err.response.text if http_err.response else 'No response content'}"
    print(review_content)
except requests.exceptions.RequestException as req_err:
    review_content = f"Error calling LLM API (RequestException): {req_err}"
    print(review_content)
except KeyError as key_err: # Should be caught by earlier checks, but as a safeguard
    review_content = f"Error: Missing critical environment variable: {key_err}. Please ensure all required variables (LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL_NAME) are set."
    print(review_content)
except Exception as e:
    review_content = f"An unexpected error occurred in the LLM script: {type(e).__name__} - {e}"
    print(review_content)
finally:
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
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
        print("Usage: python get_llm_review.py <diff_file_path> <output_file_path>")
        sys.exit(1)
    diff_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    sys.exit(get_llm_review(diff_file_path, output_file_path))