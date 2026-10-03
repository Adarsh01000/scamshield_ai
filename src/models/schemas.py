from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class UserInput(BaseModel):
    content: str = ""
    modality: str = Field(default="text", description="Modality of input: 'text', 'url', 'screenshot', 'multimodal'")
    image_bytes: Optional[bytes] = None
    image_name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Evidence(BaseModel):
    indicator: str
    detected: bool = True
    severity: str = Field(default="medium", description="'low', 'medium', 'high', 'critical'")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    source: str = Field(description="'nlp_agent', 'url_agent', 'ocr_agent', 'vision_agent'")
    evidence: str
    explanation: str

class AgentResult(BaseModel):
    agent_name: str
    evidence_list: List[Evidence] = Field(default_factory=list)
    modality_score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FinalRiskResult(BaseModel):
    risk_score: float = Field(ge=0, le=100)
    risk_level: str = "Safe"
    indicators: List[str] = Field(default_factory=list)
    evidences: List[Evidence] = Field(default_factory=list)
    modality_scores: Dict[str, float] = Field(default_factory=dict)
    explanation: str
    recommendation: str
    audit_trail: Dict[str, Any] = Field(default_factory=dict)
