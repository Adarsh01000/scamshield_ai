from typing import List, Tuple, Dict, Any, Optional
from src.models.schemas import Evidence, AgentResult
from src.core.config import settings

class RiskFusionAgent:
    """
    Risk Fusion Agent for ScamShield AI.
    Transparently fuses multi-modal evidence and individual agent scores
    into a calibrated 0-100 risk score with auditable calculation steps.
    """
    def __init__(self):
        self.weights = {
            "text": settings.WEIGHT_TEXT,
            "url": settings.WEIGHT_URL,
            "vision": settings.WEIGHT_VISION,
            "ocr": 0.20
        }
        self.correlation_boost = settings.CORRELATION_BOOST
        self.last_audit_trail: Dict[str, Any] = {}
        self.last_modality_scores: Dict[str, float] = {}

    def get_risk_level(self, score: float) -> str:
        if score >= 75.0:
            return "Severe Scam / High Risk"
        elif score >= 50.0:
            return "Suspicious / Moderate Risk"
        elif score >= 25.0:
            return "Low Risk / Caution"
        else:
            return "Safe / Negligible Risk"

    def calculate_risk(
        self,
        evidences: List[Evidence],
        agent_results: Optional[List[AgentResult]] = None
    ) -> Tuple[float, List[str]]:
        """
        Calculates unified risk score and returns (score, unique_indicators).
        Maintains backward compatibility while generating detailed audit metadata.
        """
        if not evidences and not agent_results:
            self.last_audit_trail = {
                "raw_score": 0.0,
                "multi_modal_bonus": 1.0,
                "final_score": 0.0,
                "breakdown": []
            }
            self.last_modality_scores = {"text": 0.0, "url": 0.0, "ocr": 0.0, "vision": 0.0}
            return 0.0, []

        raw_score = 0.0
        indicators = []
        breakdown = []
        sources = set()

        for ev in evidences:
            if ev.indicator not in indicators:
                indicators.append(ev.indicator)
            sources.add(ev.source)

            # Severity-weighted score contribution
            sev = ev.severity.lower()
            if sev == "critical":
                weight = 45.0
            elif sev == "high":
                weight = 40.0
            elif sev == "medium":
                weight = 20.0
            else:
                weight = 10.0

            contrib = weight * ev.confidence
            raw_score += contrib
            breakdown.append({
                "indicator": ev.indicator,
                "source": ev.source,
                "severity": ev.severity,
                "confidence": ev.confidence,
                "contribution": round(contrib, 2)
            })

        # Calculate modality-specific scores
        modality_scores: Dict[str, float] = {}
        if agent_results:
            for ar in agent_results:
                clean_name = ar.agent_name.replace("_agent", "")
                modality_scores[clean_name] = round(ar.modality_score, 1)
        else:
            # Infer from evidence sources
            for src in sources:
                clean_src = src.replace("_agent", "")
                src_evs = [e for e in evidences if e.source == src]
                src_score = sum(
                    (45 if e.severity == "critical" else 40 if e.severity == "high" else 20) * e.confidence
                    for e in src_evs
                )
                modality_scores[clean_src] = min(round(src_score, 1), 100.0)

        # Multi-modal correlation boost: if both text and URL or screenshot exhibit high risk
        applied_boost = 1.0
        active_suspicious_modalities = sum(1 for score in modality_scores.values() if score > 30.0)
        if active_suspicious_modalities >= 2:
            applied_boost = self.correlation_boost
            raw_score = raw_score * applied_boost

        final_score = min(round(raw_score, 1), 100.0)
        unique_indicators = indicators  # Preserve ordered unique indicators

        # Save audit record
        self.last_modality_scores = modality_scores
        self.last_audit_trail = {
            "formula": "Sum(severity_weight * confidence) * multi_modal_boost",
            "weights_used": self.weights,
            "raw_score": round(raw_score / applied_boost, 2),
            "multi_modal_boost": applied_boost,
            "final_score": final_score,
            "risk_level": self.get_risk_level(final_score),
            "evidence_breakdown": breakdown,
            "modality_scores": modality_scores
        }

        return final_score, unique_indicators
