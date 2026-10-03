from typing import List
from src.models.schemas import AgentResult, Evidence

SEVERITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1
}

class EvidenceAgent:
    """
    Evidence Agent for ScamShield AI.
    Converts and aggregates multi-agent outputs into a structured,
    auditable, and ranked evidence registry.
    """
    def collect_evidence(self, agent_results: List[AgentResult]) -> List[Evidence]:
        all_evidence: List[Evidence] = []
        seen = set()

        for result in agent_results:
            for ev in result.evidence_list:
                key = (ev.indicator, ev.source, ev.evidence)
                if key not in seen:
                    seen.add(key)
                    all_evidence.append(ev)

        # Sort by severity descending, then confidence descending
        all_evidence.sort(
            key=lambda x: (SEVERITY_ORDER.get(x.severity.lower(), 1), x.confidence),
            reverse=True
        )

        return all_evidence

    def summarize(self, evidences: List[Evidence]) -> dict:
        """Produce an auditable breakdown of evidence categories."""
        counts_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        sources = set()
        
        for ev in evidences:
            sev = ev.severity.lower()
            counts_by_severity[sev] = counts_by_severity.get(sev, 0) + 1
            sources.add(ev.source)

        return {
            "total_indicators": len(evidences),
            "severity_counts": counts_by_severity,
            "contributing_sources": list(sources),
            "high_critical_count": counts_by_severity.get("critical", 0) + counts_by_severity.get("high", 0)
        }
