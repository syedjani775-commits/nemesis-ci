import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

# 1. Load keys from .env
load_dotenv()

# 2. Setup Clients (Nebius Token Factory + Tavily Search)
nebius_client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.getenv("NEBIUS_API_KEY"),
)
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def run_nemesis_ci(ci_error_log: str):
    print("\n[1/3] Nemesis-CI: Ingesting CI/CD failure log...")
    
    # Extract error signature and fetch documentation via Tavily
    error_summary = ci_error_log.strip().splitlines()[-1]
    print(f"[2/3] Querying Tavily for live fix context: '{error_summary}'...")
    search_results = tavily_client.search(
        query="Python fix PyJWT KeyError algorithm decode",
        max_results=2
    )
    web_context = "\n".join([r["content"] for r in search_results["results"]])
    
    # Generate remediation patch using NVIDIA Nemotron on Nebius
    print("[3/3] Generating autonomous patch with NVIDIA Nemotron via Nebius...")
    prompt = (
        "You are Nemesis-CI, an automated DevOps test remediation agent.\n\n"
        f"CI/CD Failure Log:\n{ci_error_log}\n\n"
        f"Live Search Fix Context:\n{web_context}\n\n"
        "Output your response starting with:\n"
        "Root Cause: <1-2 sentences explaining the bug>\n"
        "Corrected Patch:\n"
        "```python\n"
        "<complete fixed code>\n"
        "```\n"
    )

    completion = nebius_client.chat.completions.create(
        model="nvidia/Nemotron-3_5-Lightning",
        messages=[
            {
                "role": "system",
                "content": "You are an expert DevOps engineer who analyzes CI/CD bugs and outputs accurate, production-ready code patches."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=4500
    )
    
    raw_output = completion.choices[0].message.content or ""
    
    # Clean the response to display only the root cause and code patch
    if "Root Cause:" in raw_output:
        clean_output = "Root Cause:" + raw_output.split("Root Cause:", 1)[-1]
        return clean_output.strip()
        
    return raw_output

if __name__ == "__main__":
    sample_log = """
FAIL: test_jwt_verification (tests.test_auth.TestAuth)
Traceback (most recent call last):
  File "/workspace/tests/test_auth.py", line 18, in test_jwt_verification
    payload = jwt.decode(token, secret, algorithms=["HS256"])
KeyError: 'algorithm'
"""
    print("--- Triggering Nemesis-CI Autonomous Incident Fixer ---")
    patch = run_nemesis_ci(sample_log)
    print("\n=== Nemesis-CI Generated Patch ===")
    print(patch)