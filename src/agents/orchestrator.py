import re
from typing import Optional, List, Dict, Any
from src.models.schemas import UserInput, Evidence, AgentResult, FinalRiskResult
from src.agents.nlp import NLPAgent
from src.agents.url import URLAgent
from src.agents.ocr import OCRAgent
from src.agents.vision import VisionAgent
from src.agents.evidence import EvidenceAgent
from src.agents.risk_fusion import RiskFusionAgent
from src.agents.explanation import ExplanationAgent

class OrchestratorAgent:
    """
    Orchestrator Agent for ScamShield AI.
    Validates user input, automatically detects or routes modality,
    coordinates specialized analysis agents (NLP, URL, OCR, Vision),
    aggregates evidence, triggers risk fusion, and produces an explainable assessment.
    """
    def __init__(self):
        self.nlp = NLPAgent()
        self.url_agent = URLAgent()
        self.ocr = OCRAgent()
        self.vision = VisionAgent()
        self.evidence_collector = EvidenceAgent()
        self.risk_fusion = RiskFusionAgent()
        self.explanation = ExplanationAgent()

    def detect_modality(self, content: str, image_bytes: Optional[bytes] = None, requested_modality: Optional[str] = None) -> str:
        """Automatically identify modality if not specified or set to auto."""
        if requested_modality and requested_modality not in ["auto", ""]:
            return requested_modality

        if image_bytes is not None or any(content.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".bmp", ".webp"]):
            return "screenshot"

        cleaned = content.strip()
        # Check if entire content is a single URL
        if cleaned.startswith(("http://", "https://", "www.")) or (
            re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?$', cleaned) and " " not in cleaned
        ):
            return "url"

        return "text"

    def analyze(
        self,
        content: str = "",
        modality: str = "text",
        image_bytes: Optional[bytes] = None,
        image_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FinalRiskResult:
        resolved_modality = self.detect_modality(content, image_bytes, modality)
        user_input = UserInput(
            content=content,
            modality=resolved_modality,
            image_bytes=image_bytes,
            image_name=image_name,
            metadata=metadata or {}
        )

        agent_results: List[AgentResult] = []

        if resolved_modality == "text":
            # 1. Analyze text with NLP Agent
            nlp_res = self.nlp.analyze(user_input)
            agent_results.append(nlp_res)

            # 2. Cross-modal: If text contains embedded URLs, route to URL Agent
            extracted_urls = nlp_res.metadata.get("extracted_urls", [])
            for url in extracted_urls:
                url_input = UserInput(content=url, modality="url")
                url_res = self.url_agent.analyze(url_input)
                agent_results.append(url_res)

        elif resolved_modality == "url":
            # Direct URL analysis
            url_res = self.url_agent.analyze(user_input)
            agent_results.append(url_res)

        elif resolved_modality == "screenshot":
            # 1. Visual OCR extraction
            ocr_res = self.ocr.analyze(user_input)
            agent_results.append(ocr_res)

            # 2. Visual layout and color analysis
            vision_res = self.vision.analyze(user_input)
            agent_results.append(vision_res)

            # 3. Cross-modal reuse: pass OCR-extracted text to NLP pipeline
            extracted_text = ocr_res.metadata.get("extracted_text", "")
            if extracted_text.strip():
                nlp_from_ocr = self.nlp.analyze(UserInput(content=extracted_text, modality="text"))
                # Label source clearly as OCR-derived text
                for ev in nlp_from_ocr.evidence_list:
                    ev.source = "ocr_nlp_agent"
                agent_results.append(nlp_from_ocr)

            # 4. Cross-modal reuse: pass OCR-extracted URLs to URL pipeline
            extracted_urls = ocr_res.metadata.get("extracted_urls", [])
            for url in extracted_urls:
                url_input = UserInput(content=url, modality="url")
                url_res = self.url_agent.analyze(url_input)
                for ev in url_res.evidence_list:
                    ev.source = "ocr_url_agent"
                agent_results.append(url_res)

        elif resolved_modality == "multimodal":
            # Simultaneous text, URL, and screenshot processing
            if user_input.content:
                if user_input.content.startswith(("http://", "https://")):
                    agent_results.append(self.url_agent.analyze(user_input))
                else:
                    nlp_res = self.nlp.analyze(user_input)
                    agent_results.append(nlp_res)
                    for url in nlp_res.metadata.get("extracted_urls", []):
                        agent_results.append(self.url_agent.analyze(UserInput(content=url, modality="url")))

            if user_input.image_bytes or user_input.image_name:
                ocr_res = self.ocr.analyze(user_input)
                agent_results.append(ocr_res)
                agent_results.append(self.vision.analyze(user_input))
                if ocr_res.metadata.get("extracted_text"):
                    agent_results.append(self.nlp.analyze(UserInput(content=ocr_res.metadata["extracted_text"], modality="text")))

        # 3. Evidence Collection & Ranking
        evidences = self.evidence_collector.collect_evidence(agent_results)

        # 4. Risk Fusion
        risk_score, indicators = self.risk_fusion.calculate_risk(evidences, agent_results)
        modality_scores = self.risk_fusion.last_modality_scores
        audit_trail = self.risk_fusion.last_audit_trail

        # 5. Grounded Explanation Generation
        final_result = self.explanation.generate_explanation(
            risk_score=risk_score,
            indicators=indicators,
            evidences=evidences,
            modality_scores=modality_scores,
            audit_trail=audit_trail
        )

        return final_result
