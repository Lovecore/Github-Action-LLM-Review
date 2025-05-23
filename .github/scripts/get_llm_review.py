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
        # Get API credentials from environment variables
        api_key = os.environ['LLM_API_KEY']
        llm_endpoint = os.environ.get('LLM_ENDPOINT')
        model_name = os.environ.get('LLM_MODEL_NAME')

        # Validate environment variables
        if not llm_endpoint or llm_endpoint == "YOUR_LLM_API_ENDPOINT_HERE":
            review_content = "Error: LLM_ENDPOINT environment variable is not set or is a placeholder. Please configure it in the GitHub Action workflow."
            print(review_content)
            with open(output_file_path, 'w') as outfile:
                outfile.write(review_content)
            return 1

        if not model_name or model_name == "YOUR_LLM_MODEL_NAME_HERE":
            review_content = "Error: LLM_MODEL_NAME environment variable is not set or is a placeholder. Please configure it."
            print(review_content)
            with open(output_file_path, 'w') as outfile:
                outfile.write(review_content)
            return 1

        # Read the diff file
        with open(diff_file_path, 'r', encoding='utf-8') as f:
            diff_content = f.read()

        # Check if diff is empty
        if not diff_content.strip():
            print("No code changes detected in the diff. Skipping LLM review.")
            review_content = "No code changes detected to review."
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                outfile.write(review_content)
            return 0

        # Prepare the prompt for the LLM
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
```

Review:
"""

        # Prepare headers for API request
        headers = {
            "Authorization": f"Bearer {api_key}",  # Common for many APIs using Bearer tokens
            "Content-Type": "application/json"    # Standard Content-Type for JSON APIs
        }

        # Prepare payload for API request (adapt to your LLM provider)
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],  # Common pattern for chat models
            "max_tokens": 3000,                                   # Adjust based on expected review length
            "temperature": 0.2                                    # Lower for more deterministic reviews
        }

        # Send request to LLM API
        print(f"Sending request to LLM endpoint: {llm_endpoint} with model: {model_name}")
        response = requests.post(llm_endpoint, headers=headers, json=payload, timeout=300)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse the LLM response
        response_data = response.json()
        
        # Extract review text based on LLM provider format
        # OpenAI format
        if 'choices' in response_data and response_data['choices'] and 'message' in response_data['choices'][0] and 'content' in response_data['choices'][0]['message']:
            review_text = response_data['choices'][0]['message']['content']
        # Anthropic Claude format
        elif 'content' in response_data and response_data['content'] and len(response_data['content']) > 0 and 'text' in response_data['content'][0]:
            review_text = response_data['content'][0]['text']
        # Generic fallback
        else:
            review_text = f"Error: Could not parse review from LLM response using common patterns. Raw response:\n{json.dumps(response_data, indent=2)}"

        review_content = review_text.strip()
        
    except KeyError as key_err:
        # Handle missing environment variables
        review_content = f"Error: Missing critical environment variable: {key_err}. Please ensure all required variables (LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL_NAME) are set."
        print(review_content)
    except json.JSONDecodeError as json_err:
        # Handle invalid JSON response
        review_content = f"Error parsing LLM JSON response: {json_err}. \nRaw response text:\n{response.text if 'response' in locals() else 'No response available'}"
        print(review_content)
    except requests.exceptions.Timeout:
        # Handle timeout errors
        review_content = "Error: The request to the LLM API timed out after 5 minutes."
        print(review_content)
    except requests.exceptions.HTTPError as http_err:
        # Handle HTTP errors
        review_content = f"HTTP error occurred: {http_err}\nResponse Content: {http_err.response.text if hasattr(http_err, 'response') and http_err.response else 'No response content'}"
        print(review_content)
    except requests.exceptions.RequestException as req_err:
        # Handle other request errors
        review_content = f"Error calling LLM API: {req_err}"
        print(review_content)
    except Exception as e:
        # Handle any other unexpected errors
        review_content = f"An unexpected error occurred: {type(e).__name__} - {e}"
        print(review_content)
    finally:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Write results to output file
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            outfile.write(review_content)
        
        # Report result
        if "Error:" in review_content:
            print(f"LLM review script finished with errors. Output written to {output_file_path}")
            return 1
        else:
            print(f"Review successfully generated and written to {output_file_path}")
            return 0

# Main entry point
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python get_llm_review.py <diff_file_path> <output_file_path>")
        sys.exit(1)
    
    diff_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    exit_code = get_llm_review(diff_file_path, output_file_path)
    sys.exit(exit_code)
