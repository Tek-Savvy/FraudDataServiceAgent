# FraudDataServiceAgent
Autonomous Fraud Triaging Agent Solution
This repository contains the full production architecture for the Autonomous AI Fraud Triaging Agent.
Architecture Structure
`python_agent_service/`: FastAPI + LangChain/LangGraph + Azure OpenAI service handling multi-agent orchestration, PII masking, and RAG.
`dotnet_data_service/`: C# .NET 8 Web API providing core ledger and account profile data from Oracle/SQL databases.
`docker-compose.yml`: Container orchestration setup.
Quick Start
Configure `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` in `python_agent_service/config.py` or via environment variables.
Run with Docker Compose:
```bash
   docker-compose up --build
   ```
