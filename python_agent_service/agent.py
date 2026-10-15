import httpx
from typing import TypedDict, List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings
from schemas import AlertRequest, CustomerProfile, FraudAnalysisReport
from anonymizer import PIIAnonymizer

class AgentState(TypedDict):
    alert: AlertRequest
    sanitized_notes: str
    pii_mapping: dict
    customer_profile: CustomerProfile
    historical_matches: List[str]
    report: FraudAnalysisReport

anonymizer = PIIAnonymizer()

async def fetch_customer_profile(account_id: str) -> CustomerProfile:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.DOTNET_SERVICE_URL}/account/{account_id}")
            if response.status_code == 200:
                return CustomerProfile(**response.json())
        except Exception:
            pass
        return CustomerProfile(account_id=account_id, account_age_days=30, historical_risk_score=0.5, average_monthly_spend=500.0)

async def search_historical_fraud_patterns(merchant: str) -> List[str]:
    return [
        f"Match pattern: Rapid transaction velocity detected at {merchant}",
        "Match pattern: Cross-border structured wire transfer under €10,000 threshold"
    ]

async def generate_fraud_report_node(state: AgentState) -> AgentState:
    llm = AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        openai_api_key=settings.AZURE_OPENAI_API_KEY,
        openai_api_version="2024-02-15-preview",
        temperature=0.0
    )
    
    structured_llm = llm.with_structured_output(FraudAnalysisReport)

    system_prompt = (
        "You are an expert Banking Fraud Triaging Agent. Evaluate the risk of the transaction based on "
        "customer profile and historical fraud patterns. Always output structured JSON strictly matching the schema."
    )

    user_prompt = f"""
    Alert ID: {state['alert'].alert_id}
    Transaction Amount: €{state['alert'].transaction_amount}
    Merchant: {state['alert'].merchant_name}
    Sanitized Notes: {state['sanitized_notes']}
    
    Customer Profile:
    - Account Age: {state['customer_profile'].account_age_days} days
    - Historical Risk Score: {state['customer_profile'].historical_risk_score}
    - Average Monthly Spend: €{state['customer_profile'].average_monthly_spend}
    
    Historical Matches: {', '.join(state['historical_matches'])}
    """

    report: FraudAnalysisReport = await structured_llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    rehydrated_reasoning = [
        anonymizer.rehydrate(step, state['pii_mapping']) for step in report.reasoning
    ]
    report.reasoning = rehydrated_reasoning

    state['report'] = report
    return state
