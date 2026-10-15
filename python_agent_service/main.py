import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from schemas import AlertRequest, FraudAnalysisReport
from anonymizer import PIIAnonymizer
from agent import (
    AgentState,
    fetch_customer_profile,
    search_historical_fraud_patterns,
    generate_fraud_report_node
)

app = FastAPI(title="Autonomous AI Fraud Triaging Agent Service")
anonymizer = PIIAnonymizer()

@app.post("/api/v1/triage-alert", response_model=FraudAnalysisReport)
async def triage_alert(alert: AlertRequest):
    try:
        sanitized_notes, pii_map = anonymizer.sanitize(alert.raw_notes or "")

        profile_task = fetch_customer_profile(alert.account_id)
        vector_task = search_historical_fraud_patterns(alert.merchant_name)
        
        customer_profile, historical_matches = await asyncio.gather(profile_task, vector_task)

        initial_state: AgentState = {
            "alert": alert,
            "sanitized_notes": sanitized_notes,
            "pii_mapping": pii_map,
            "customer_profile": customer_profile,
            "historical_matches": historical_matches,
            "report": None
        }

        final_state = await generate_fraud_report_node(initial_state)

        return final_state['report']

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
