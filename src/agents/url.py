import os
import joblib
import pandas as pd
from typing import List, Optional
from src.models.schemas import UserInput, Evidence, AgentResult
from src.agents.url_features import extract_url_features

class URLAgent:
    """
    URL Agent for ScamShield AI.
    Extracts lexical, structural, and entropy features from URLs,
    runs a trained Random Forest classifier, and synthesizes auditable evidence.
    """
    def __init__(self, model_path: Optional[str] = None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "..", "models", "url_classifier.joblib")
        self.model_path = os.path.abspath(model_path)
        self.model = None
        self.feature_names = None
        self.model_metrics = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                payload = joblib.load(self.model_path)
                self.model = payload.get("model")
                self.feature_names = payload.get("feature_names")
                self.model_metrics = payload.get("metrics")
            except Exception as e:
                print(f"[URLAgent] Warning: could not load trained model ({e}). Using heuristics.")
                self.model = None

    def analyze(self, user_input: UserInput) -> AgentResult:
        url = user_input.content.strip()
        evidence_list: List[Evidence] = []
        
        if not url:
            return AgentResult(agent_name="url_agent", evidence_list=[], modality_score=0.0)

        # 1. Extract features
        extracted = extract_url_features(url)
        feats = extracted["features"]
        meta = extracted["metadata"]

        # 2. Predict with ML model if available
        ml_prob = 0.0
        if self.model and self.feature_names:
            try:
                df_feat = pd.DataFrame([feats])[self.feature_names]
                probs = self.model.predict_proba(df_feat)[0]
                # Probability of scam (class 1)
                ml_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
            except Exception as e:
                print(f"[URLAgent] Inference error: {e}")
                ml_prob = 0.0

        # Heuristic fallback if model unavailable
        if self.model is None:
            heuristic_score = 0.0
            if meta["has_ip"]:
                heuristic_score += 0.4
            if meta["has_suspicious_tld"]:
                heuristic_score += 0.3
            if meta["matched_keywords"]:
                heuristic_score += min(0.3, len(meta["matched_keywords"]) * 0.1)
            ml_prob = min(heuristic_score, 0.95)

        # 3. Formulate Evidence Items

        # Indicator: ML Phishing Classification
        if ml_prob >= 0.50:
            evidence_list.append(Evidence(
                indicator="ml_url_phishing_risk",
                detected=True,
                severity="critical" if ml_prob >= 0.85 else "high",
                confidence=round(ml_prob, 2),
                source="url_agent",
                evidence=f"ML Classifier predicted {ml_prob * 100:.1f}% phishing probability (RF model).",
                explanation="Statistical and structural lexical features match known malicious and deceptive domains."
            ))

        # Indicator: IP Address Host
        if meta["has_ip"]:
            evidence_list.append(Evidence(
                indicator="ip_address_host",
                detected=True,
                severity="critical",
                confidence=0.96,
                source="url_agent",
                evidence=f"Raw IP host: {meta['hostname']}",
                explanation="Legitimate institutions use registered domain names. Bare IP addresses indicate illicit evasion."
            ))

        # Indicator: Suspicious TLD
        if meta["has_suspicious_tld"]:
            tld = "." + meta["hostname"].split(".")[-1] if "." in meta["hostname"] else "unknown"
            evidence_list.append(Evidence(
                indicator="suspicious_tld",
                detected=True,
                severity="high",
                confidence=0.88,
                source="url_agent",
                evidence=f"Domain registered under high-abuse TLD: '{tld}'",
                explanation="Disproportionately abused by phishing kits due to cheap or anonymous bulk registration."
            ))

        # Indicator: Sensitive Authentication / Banking Keywords in Domain or Path
        if meta["matched_keywords"]:
            evidence_list.append(Evidence(
                indicator="phishing_keywords_in_url",
                detected=True,
                severity="high" if len(meta["matched_keywords"]) >= 2 else "medium",
                confidence=0.85,
                source="url_agent",
                evidence=f"Suspicious terms found: {', '.join(meta['matched_keywords'][:4])}",
                explanation="Deceptive URLs mimic authentic login, verification, and banking endpoints to steal credentials."
            ))

        # Indicator: Excessive Subdomains
        if feats["num_subdomains"] >= 3:
            evidence_list.append(Evidence(
                indicator="excessive_subdomains",
                detected=True,
                severity="medium",
                confidence=0.78,
                source="url_agent",
                evidence=f"Number of subdomains: {feats['num_subdomains']}",
                explanation="Excessive subdomains are commonly employed to spoof brands and obscure the true domain host."
            ))

        # Indicator: High Shannon Entropy (DGA or obfuscation)
        if feats["entropy"] > 4.2 and len(url) > 30:
            evidence_list.append(Evidence(
                indicator="high_entropy_url",
                detected=True,
                severity="medium",
                confidence=0.76,
                source="url_agent",
                evidence=f"Shannon character entropy: {feats['entropy']:.2f}",
                explanation="Abnormal randomness in URL characters suggests algorithmically generated domains or token evasion."
            ))

        # Indicator: Insecure protocol with sensitive targets
        if not meta["is_https"] and meta["matched_keywords"]:
            evidence_list.append(Evidence(
                indicator="insecure_protocol",
                detected=True,
                severity="medium",
                confidence=0.80,
                source="url_agent",
                evidence="Unencrypted HTTP protocol used for sensitive authentication/banking target",
                explanation="Legitimate financial or identity services mandate TLS/HTTPS encryption."
            ))

        # 4. Modality Risk Score Calculation
        if evidence_list:
            modality_score = max(ml_prob * 100.0, 15.0)
            if any(ev.severity == "critical" for ev in evidence_list):
                modality_score = max(modality_score, 85.0)
            elif any(ev.severity == "high" for ev in evidence_list):
                modality_score = max(modality_score, 65.0)
            modality_score = min(round(modality_score, 1), 100.0)
        else:
            modality_score = round(ml_prob * 100.0, 1)

        return AgentResult(
            agent_name="url_agent",
            evidence_list=evidence_list,
            modality_score=modality_score,
            metadata={
                "features": feats,
                "ml_probability": round(ml_prob, 4),
                "hostname": meta["hostname"]
            }
        )
