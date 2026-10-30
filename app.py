import os
import time
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
st.caption("Nebius x NVIDIA AI Hackathon • **Coding & Agentic Engineering** Track • **Best Use of Tavily** Contender")

st.markdown("---")

# Benchmark Scenario Selector
scenario = st.selectbox(
    "🎯 Select CI Benchmark Scenario:",
    ["Scenario 1: PyJWT v2+ Compatibility Decode Failure", "Scenario 2: Business Logic Math Mismatch"]
)

target_test = "test_sample.py" if "Scenario 1" in scenario else "test_calc.py"
target_file = "sample_app.py" if "Scenario 1" in scenario else "sample_calc.py"

col_left, col_right = st.columns([1, 1], gap="medium")

def run_tests(test_script):
    start = time.time()
    res = subprocess.run(["python", test_script], capture_output=True, text=True)
    duration = round(time.time() - start, 3)
    return res.returncode, res.stderr or res.stdout, duration

with col_left:
    st.header("1. CI/CD Pipeline Monitor")
    st.markdown(f"Targeting verification suite: `{target_test}`")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        run_btn = st.button("▶ Run CI Pipeline Tests", use_container_width=True, type="secondary")
    with col_btn2:
        reset_btn = st.button("🔄 Reset Buggy State", use_container_width=True)

    if reset_btn:
        if "Scenario 1" in scenario:
            with open("sample_app.py", "w") as f:
                f.write("import jwt\n\ndef verify_token(token: str, secret: str):\n    return jwt.decode(token, secret)\n")
        else:
            with open("sample_calc.py", "w") as f:
                f.write("def calculate_discount(price: float, discount_pct: float) -> float:\n    return price - discount_pct\n")
        st.session_state["error_log"] = None
        st.info("Environment reset to intentional failing state.")

    if run_btn:
        code, output, duration = run_tests(target_test)
        if code != 0:
            st.error(f"🚨 Build Status: FAILED (Exit Code {code}) • Executed in {duration}s")
            st.code(output, language="bash")
            st.session_state["error_log"] = output
        else:
            st.success(f"✅ Build Status: PASSED (Clean Exit) • Executed in {duration}s")
            st.code(output, language="bash")
            st.session_state["error_log"] = None

with col_right:
    st.header("2. Autonomous Remediation Engine")
    st.markdown("Grounding with **Tavily Search API** $\\rightarrow$ **NVIDIA Nemotron-3.5** on **Nebius Token Factory**")
    
    if st.session_state.get("error_log"):
        st.warning("Action Required: Active pipeline failure captured.")
        
        if st.button("🚀 Trigger Nemesis-CI Self-Healing", type="primary", use_container_width=True):
            error_log = st.session_state["error_log"]
            error_line = error_log.strip().splitlines()[-1]
            
            with st.status("Executing Multi-Agent Self-Healing Pipeline...", expanded=True) as status:
                # Stage 1: Tavily Search
                tav_start = time.time()
                st.write("🔍 **Tavily Search API**: Querying real-time technical documentation...")
                query_str = f"Python fix {error_line} {target_file}"
                search_results = tavily_client.search(query=query_str, max_results=2)
                tav_duration = round(time.time() - tav_start, 2)
                web_context = "\n".join([r["content"] for r in search_results["results"]])
                st.write(f"✅ Context retrieved in {tav_duration}s via Tavily.")

                # Tavily Evidence Cards
                for r in search_results["results"]:
                    st.markdown(f"- 📄 **[{r['title']}]({r['url']})**: `{r['content'][:120]}...`")

                # Stage 2: Nemotron Synthesis
                st.write("🧠 **NVIDIA Nemotron-3.5**: Synthesizing targeted patch on Nebius Token Factory...")
                nem_start = time.time()
                with open(target_file, "r") as f:
                    broken_code = f.read()

                prompt = f"""You are Nemesis-CI, an autonomous DevOps repair agent.
Source File ({target_file}):
{broken_code}

Pipeline Failure Traceback:
{error_log}

Live Search Fix Context:
{web_context}

Provide the complete replacement code for {target_file} inside a single python markdown block (```python ... ```).
Only output the corrected python code.
"""
                completion = nebius_client.chat.completions.create(
                    model="nvidia/Nemotron-3_5-Lightning",
                    messages=[
                        {"role": "system", "content": "You are a senior software engineer. Output minimal, working code inside ```python blocks."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2500
                )
                nem_duration = round(time.time() - nem_start, 2)
                raw_patch = completion.choices[0].message.content or ""
                code_blocks = re.findall(r"```python(.*?)```", raw_patch, flags=re.DOTALL)
                clean_patch = code_blocks[-1].strip() if code_blocks else raw_patch

                # Stage 3: Patch & Verification
                st.write(f"💾 **File Dispatch**: Applying patch to `{target_file}` (Inference: {nem_duration}s)...")
                with open(target_file, "w") as f:
                    f.write(clean_patch)

                st.write(f"🔄 **Automated CI Re-Execution**: Verifying against `{target_test}`...")
                retest_code, retest_out, ver_duration = run_tests(target_test)

                if retest_code == 0:
                    status.update(label="Remediation Verified & Pipeline Restored!", state="complete", expanded=False)
                    st.success(f"🎉 PIPELINE RESTORED! Tests passed cleanly in {ver_duration}s.")
                    
                    st.subheader("Observability & Patch Telemetry")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Tavily Search Time", f"{tav_duration}s")
                    m2.metric("Nemotron Latency", f"{nem_duration}s")
                    m3.metric("Verification Time", f"{ver_duration}s")

                    st.subheader("Autonomous Patch Verification (Code Diff)")
                    diff = difflib.unified_diff(
                        broken_code.splitlines(keepends=True),
                        clean_patch.splitlines(keepends=True),
                        fromfile=f"{target_file} (Broken)",
                        tofile=f"{target_file} (Patched)"
                    )
                    st.code("".join(diff), language="diff")
                else:
                    status.update(label="Remediation Failed", state="error")
                    st.error("Patch applied, but verification tests failed.")
    else:
        st.info("Pipeline is healthy. No active failures detected.")