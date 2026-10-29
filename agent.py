import os
import re
import subprocess
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


def execute_pipeline():
  """Runs the CI test suite and captures output."""
  process = subprocess.run(
      ["python", "test_sample.py"], capture_output=True, text=True
  )
  return process.returncode, process.stderr or process.stdout


def heal_code(ci_error_log: str):
  print("\n[Step 1/4] Intercepted CI/CD failure log from pipeline.")

  # Live Search via Tavily
  error_summary = ci_error_log.strip().splitlines()[-1]
  print(
      f"[Step 2/4] Querying Tavily Search API for real-time fix:"
      f" '{error_summary}'..."
  )
  search_results = tavily_client.search(
      query=f"Python fix PyJWT {error_summary}", max_results=2
  )
  web_context = "\n".join([r["content"] for r in search_results["results"]])

  # Read buggy source code
  with open("sample_app.py", "r") as f:
    broken_code = f.read()

  # NVIDIA Nemotron Inference via Nebius Token Factory
  print(
      "[Step 3/4] Prompting NVIDIA Nemotron-3.5 via Nebius Token Factory for"
      " patch..."
  )
  prompt = f"""You are Nemesis-CI, an autonomous DevOps self-healing agent.
A continuous integration test has failed.

Broken Code (sample_app.py):
{broken_code}

Failure Log:
{ci_error_log}

Live Search Fix Context:
{web_context}

Provide the complete replacement code for sample_app.py inside a single python markdown block (```python ... ```).
Include all necessary imports and the fixed verify_token function with algorithms=['HS256'].
"""

  completion = nebius_client.chat.completions.create(
      model="nvidia/Nemotron-3_5-Lightning",
      messages=[
          {
              "role": "system",
              "content": (
                  "You are an automated CI/CD remediation agent. Output only"
                  " production-ready code inside ```python blocks."
              ),
          },
          {"role": "user", "content": prompt},
      ],
      temperature=0.1,
      max_tokens=4000,
  )

  raw_output = completion.choices[0].message.content or ""

  # Extract Python code block
  code_blocks = re.findall(r"```python(.*?)```", raw_output, flags=re.DOTALL)
  if code_blocks:
    return code_blocks[-1].strip()
  return raw_output


if __name__ == "__main__":
  print("=" * 65)
  print("   NEMESIS-CI: AUTONOMOUS CI/CD HEALING DEMO")
  print("   Engine: NVIDIA Nemotron-3_5-Lightning on Nebius Token Factory")
  print("   Search: Tavily Real-Time Web Context")
  print("=" * 65)

  print("\n>>> Stage 1: Running Initial CI Test Suite...")
  code, output = execute_pipeline()

  if code == 0:
    print("[Status] All tests pass. Pipeline is green.")
  else:
    print("\n[FAILURE DETECTED] CI pipeline broke with error:\n")
    print(output.strip())

    # Trigger autonomous agent
    patch = heal_code(output)

    # Write patch autonomously to disk
    print("\n[Step 4/4] Writing autonomous patch to sample_app.py...")
    with open("sample_app.py", "w") as f:
      f.write(patch)

    print("\n>>> Stage 2: Re-executing CI Pipeline to Verify Remediation...")
    retest_code, retest_output = execute_pipeline()

    if retest_code == 0:
      print("\n" + "=" * 65)
      print("  SUCCESS: PIPELINE RESTORED! Tests passed cleanly.")
      print("=" * 65)
    else:
      print("\n[Status] Pipeline still failing. Output:")
      print(retest_output)