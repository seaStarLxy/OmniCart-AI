# OmniCart-AI Testing Guide

This guide explains how to start the backend service and run the comprehensive integration test suite. This testing framework automatically verifies all routing, NLP, validation, and PII masking behaviors across all 6 agents.

## 1. Environment Setup

Ensure you have your SiliconFlow (or OpenAI) API key ready.
Set it in your terminal before running the tests:

**Windows (PowerShell)**:
```powershell
$env:SILICONFLOW_API_KEY="your_api_key_here"
```

**macOS/Linux (Bash)**:
```bash
export SILICONFLOW_API_KEY="your_api_key_here"
```

## 2. Start the Backend API Server

The test suite requires the FASTAPI application to be running locally on port `8001`.

Open a terminal, navigate to the `OmniCart-AI` directory, and run the server:
```bash
cd OmniCart-AI
uvicorn main:app --host 127.0.0.1 --port 8001
```
Leave this terminal open.

*(Note: If you encounter an "Address already in use" error, it means the server is already running in the background).*

## 3. Run the Automated Test Suite

Open a **new** terminal window, navigate to the `OmniCart-AI` directory, and execute the test runner:

```bash
cd OmniCart-AI
python test_integration.py
```

### What `test_integration.py` Does:
It sends HTTP requests to your local running API and automatically verifies the output of 16 different edge cases, including:
* **Agent 1 (Router):** Verifies queries are correctly assigned to the RAG or Order agent based on conversational context.
* **Agent 2 (RAG):** Verifies that ambiguous requests fetch expected mock-database products (e.g., "music headphones" matches "Sony Noise-canceling").
* **Agent 3 (Order):** Verifies standard order tracking flows and unknown order handling.
* **Agent 4 (Empathy):** Injects emotionally charged language ("terrible service", "frustrated") to ensure the system escalates the ticket and outputs empathy keywords.
* **Agent 5 (Security):** Tests malicious code injection blocks and ensures 11-digit PII phone numbers are obfuscated (e.g. `138****XXXX`).
* **Agent 6 (Fairness):** Validates that dialogue states successfully flush to `logs/audit_logs.json`.
* **Multi-Turn Scenarios:** Tests agent context switching mid-conversation.

### Expected Output:
You should see all cases passing with a final output stating `Result: ALL TEST CASES PASSED SUCCESSFULLY. (16 / 16)`