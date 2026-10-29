import os
import subprocess
import re
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

# Page configuration
st.set_page_config(
    page_title="Nemesis-CI Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Load environment keys
load_dotenv()

# Clients
nebius_client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.getenv("NEBIUS_API_KEY"),
)
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

st.title("⚡ Nemesis-CI: Autonomous CI/CD Failure Remediation Agent")
st.caption("Powered by **NVIDIA Nemotron-3.5-Lightning** on **Nebius Token Factory** & **Tavily Search API**")

st.divider()

col1, col2 = st.columns(2)

def run_tests():
    res = subprocess.run(["python", "test_sample.py"], capture_output=True, text=True)
    return res.returncode, res.stderr or res.stdout

with col1:
    st.subheader("1. CI/CD Pipeline Monitor")
    if st.button("Run CI Pipeline Tests", use_container_width=True):
        code, output = run_tests()
        if code != 0:
            st.error("🚨 Build Status: FAILED (Tests Broken)")
            st.code(output, language="bash")
            st.session_state["error_log"] = output
        else:
            st.success("✅ Build Status: PASSED (Pipeline Green)")
            st.code(output, language="bash")
            st.session_state["error_log"] = None

with col2:
    st.subheader("2. Autonomous Remediation Engine")
    if st.session_state.get("error_log"):
        st.warning("Action Required: Build failure detected. Autonomous agent standing by.")
        
        if st.button("🚀 Trigger Nemesis-CI Self-Healing", type="primary", use_container_width=True):
            error_log = st.session_state["error_log"]
            error_line = error_log.strip().splitlines()[-1]
            
            with st.status("Executing Agentic Self-Healing Loop...", expanded=True) as status:
                st.write("🔍 **Tavily Search**: Retrieving live documentation and fix signatures...")
                search_results = tavily_client.search(
                    query=f"Python fix PyJWT {error_line}",
                    max_results=2
                )
                web_context = "\n".join([r["content"] for r in search_results["results"]])
                st.write("✅ Context retrieved from Tavily.")

                st.write("🧠 **NVIDIA Nemotron-3.5**: Synthesizing patch via Nebius Token Factory...")
                with open("sample_app.py", "r") as f:
                    broken_code = f.read()

                prompt = f"""You are Nemesis-CI, an autonomous DevOps self-healing agent.
Broken Code (sample_app.py):
{broken_code}

Failure Log:
{error_log}

Live Search Fix Context:
{web_context}

Provide the complete replacement code for sample_app.py inside a single python markdown block (```python ... ```).
Include all necessary imports and the fixed verify_token function with algorithms=['HS256'].
"""
                completion = nebius_client.chat.completions.create(
                    model="nvidia/Nemotron-3_5-Lightning",
                    messages=[
                        {"role": "system", "content": "Output only production-ready code inside ```python blocks."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=4000
                )
                raw_patch = completion.choices[0].message.content or ""
                code_blocks = re.findall(r"```python(.*?)```", raw_patch, flags=re.DOTALL)
                clean_patch = code_blocks[-1].strip() if code_blocks else raw_patch

                st.write("💾 **Agent Dispatch**: Overwriting broken source file with validated patch...")
                with open("sample_app.py", "w") as f:
                    f.write(clean_patch)

                st.write("🔄 **Re-executing CI Pipeline** to verify patch...")
                retest_code, retest_out = run_tests()

                if retest_code == 0:
                    status.update(label="Build Restored Successfully!", state="complete", expanded=False)
                    st.success("🎉 PIPELINE RESTORED! Autonomous Patch Applied & Tests Passed.")
                    st.subheader("Generated Patch:")
                    st.code(clean_patch, language="python")
                else:
                    status.update(label="Remediation Failed", state="error")
                    st.error("Patch applied but tests still failing.")
    else:
        st.info("Pipeline is clean or has not been triggered yet.")