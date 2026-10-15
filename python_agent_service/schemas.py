from pydantic import BaseModel, Field
from typing import List, Optional

class AlertRequest(BaseModel):
    alert_id: str = Field(description="Unique fraud alert ID")
    account_id: str = Field(description="Customer account identifier")
    transaction_amount: float = Field(description="Transaction amount in EUR")
    merchant_name: str = Field(description="Name of merchant or recipient")
    raw_notes: Optional[str] = Field(default="", description="Unstructured transaction notes/evidence")

class CustomerProfile(BaseModel):
    account_id: str
    account_age_days: int
    historical_risk_score: float
    average_monthly_spend: float

class FraudAnalysisReport(BaseModel):
    alert_id: str
    risk_score: float = Field(description="Calculated fraud risk score from 0.0 (Safe) to 1.0 (High Fraud Risk)")
    verdict: str = Field(description="RECOMMEND_CLOSE or RECOMMEND_ESCALATE")
    reasoning: List[str] = Field(description="Step-by-step audit reasoning for the decision")
    recommended_action: str = Field(description="Immediate action recommended for analysts")
