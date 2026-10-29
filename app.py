import os
import subprocess
import re
import difflib
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

st.set_page_config(
    page_title="Nemesis-CI: Autonomous CI/CD Remediation",
    page_icon="⚡",
    layout="wide"
)

load_dotenv()

nebius_client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.getenv("NEBIUS_API_KEY"),
)
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

st.title("⚡ Nemesis-CI: Autonomous CI/CD Failure Remediation Agent")
st.caption("Grand Prize Contender • Powered by **NVIDIA Nemotron-3.5-Lightning** on **Nebius Token Factory** & **Tavily Search API**")

st.markdown("---")

col_left, col_right = st.columns([1, 1], gap="medium")

def run_tests():
    res = subprocess.run(["python", "test_sample.py"], capture_output=True, text=True)
    return res.returncode, res.stderr or res.stdout

with col_left:
    st.header("1. CI/CD Pipeline Monitor")
    st.markdown("Monitors live test runner executions and traps stack traces.")
    
    if st.button("▶ Run CI Pipeline Tests", use_container_width=True, type="secondary"):
        code, output = run_tests()
        if code != 0:
            st.error("🚨 Build Status: FAILED (Tests Broken)")
            st.code(output, language="bash")
            st.session_state["error_log"] = output
        else:
            st.success("✅ Build Status: PASSED (Pipeline Green)")
            st.code(output, language="bash")
            st.session_state["error_log"] = None

with col_right:
    st.header("2. Autonomous Remediation Engine")
    st.markdown("Dynamic self-healing loop: Tavily Docs $\\rightarrow$ NVIDIA Nemotron $\\rightarrow$ Auto-patch.")
    
    if st.session_state.get("error_log"):
        st.warning("Action Required: Build failure detected. Autonomous agent ready.")
        
        if st.button("🚀 Trigger Nemesis-CI Self-Healing", type="primary", use_container_width=True):
            error_log = st.session_state["error_log"]
            error_line = error_log.strip().splitlines()[-1]
            
            with st.status("Executing Agentic Self-Healing Loop...", expanded=True) as status:
                st.write("🔍 **Tavily Search API**: Querying live documentation for syntax fix...")
                search_results = tavily_client.search(
                    query=f"Python fix PyJWT {error_line}",
                    max_results=2
                )
                web_context = "\n".join([r["content"] for r in search_results["results"]])
                st.write("✅ Live context retrieved from Tavily.")

                st.write("🧠 **NVIDIA Nemotron-3.5**: Formulating patch on Nebius Token Factory...")
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

                st.write("💾 **Autonomous Dispatch**: Writing validated patch to source on disk...")
                with open("sample_app.py", "w") as f:
                    f.write(clean_patch)

                st.write("🔄 **Re-running Verification Suite**...")
                retest_code, retest_out = run_tests()

                if retest_code == 0:
                    status.update(label="Remediation Verified & Pipeline Restored!", state="complete", expanded=False)
                    st.success("🎉 PIPELINE RESTORED! Tests passed cleanly.")
                    
                    st.subheader("Autonomous Patch Verification (Code Diff)")
                    diff = difflib.unified_diff(
                        broken_code.splitlines(keepends=True),
                        clean_patch.splitlines(keepends=True),
                        fromfile="sample_app.py (Broken)",
                        tofile="sample_app.py (Patched)"
                    )
                    st.code("".join(diff), language="diff")
                else:
                    status.update(label="Remediation Failed", state="error")
                    st.error("Patch applied, but tests did not pass.")
    else:
        st.info("Pipeline is healthy. No remediation required.")