# Nemesis-CI: Autonomous CI/CD Failure Remediation Agent

Built for the **Nebius x NVIDIA Global AI Hackathon**  
*Track: Coding and Agentic Engineering*

## Overview
Nemesis-CI is an agentic DevOps tool that intercepts broken CI/CD pipelines, diagnoses the root cause of test/build failures using real-time search context, and automatically generates production-ready code patches.

## Tech Stack & Compliance
- **Inference Infrastructure:** Nebius Token Factory (Serverless OpenAI-compatible API)
- **Model:** `nvidia/Nemotron-3_5-Lightning` (NVIDIA Open Model)
- **Live Search & Tool Calling:** Tavily Search API
- **Runtime:** Python 3.12+

## Architecture Flow
1. **Ingest:** Intercepts raw CI/CD traceback/stdout logs.
2. **Context Retrieval:** Dispatches targeted error signatures to Tavily to retrieve current framework fixes and documentation.
3. **Reasoning & Patching:** Prompts NVIDIA Nemotron on Nebius with the combined log and web context to generate an autonomous remediation patch.

## Quickstart
```bash
# Clone the repository
git clone https://github.com/your-username/nemesis-ci.git
cd nemesis-ci

# Install dependencies
pip install openai tavily-python python-dotenv

# Configure environment variables (.env)
NEBIUS_API_KEY=your_nebius_key
TAVILY_API_KEY=your_tavily_key

# Run the remediation agent
python agent.py