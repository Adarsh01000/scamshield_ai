import os
import sys
from typing import Dict, Any, List, Tuple
from src.agents.orchestrator import OrchestratorAgent
from src.agents.url import URLAgent
from src.agents.nlp import NLPAgent
from src.models.schemas import UserInput
from src.data.evaluation_dataset import (
    TEXT_EVALUATION_DATA,
    URL_EVALUATION_DATA,
    MULTIMODAL_EVALUATION_DATA
)

def compute_binary_metrics(y_true: List[int], y_pred: List[int]) -> Dict[str, Any]:
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)

    total = max(1, len(y_true))
    accuracy = (tp + tn) / total
    precision = tp / max(1, tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / max(1, tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / max(1e-6, precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "total_samples": len(y_true),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": [[tn, fp], [fn, tp]]
    }

class EvaluationAgent:
    """
    Evaluation Agent for ScamShield AI.
    Runs repeatable, deterministic test benchmarks, computes confusion matrices,
    precision, recall, F1-scores, false positive/negative audits, and ablation experiments.
    """
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.url_agent = URLAgent()
        self.nlp = NLPAgent()

    def evaluate_text_pipeline(self, threshold: float = 40.0) -> Dict[str, Any]:
        y_true = []
        y_pred = []
        details = []
        false_positives = []
        false_negatives = []

        for item in TEXT_EVALUATION_DATA:
            res = self.orchestrator.analyze(item["text"], modality="text")
            pred = 1 if res.risk_score >= threshold else 0
            label = item["label"]
            y_true.append(label)
            y_pred.append(pred)

            record = {
                "id": item["id"],
                "type": item["type"],
                "text_snippet": item["text"][:70] + "...",
                "ground_truth": "Scam" if label == 1 else "Legitimate",
                "predicted": "Scam" if pred == 1 else "Legitimate",
                "risk_score": res.risk_score,
                "indicators": res.indicators
            }
            details.append(record)

            if label == 0 and pred == 1:
                false_positives.append(record)
            elif label == 1 and pred == 0:
                false_negatives.append(record)

        metrics = compute_binary_metrics(y_true, y_pred)
        metrics["false_positives"] = false_positives
        metrics["false_negatives"] = false_negatives
        metrics["records"] = details
        return metrics

    def evaluate_url_pipeline(self, threshold: float = 40.0) -> Dict[str, Any]:
        y_true = []
        y_pred = []
        details = []

        for url, label in URL_EVALUATION_DATA:
            res = self.url_agent.analyze(UserInput(content=url, modality="url"))
            pred = 1 if res.modality_score >= threshold else 0
            y_true.append(label)
            y_pred.append(pred)

            details.append({
                "url": url,
                "ground_truth": "Phishing" if label == 1 else "Legitimate",
                "predicted": "Phishing" if pred == 1 else "Legitimate",
                "score": res.modality_score,
                "indicators": [e.indicator for e in res.evidence_list]
            })

        metrics = compute_binary_metrics(y_true, y_pred)
        metrics["records"] = details
        return metrics

    def run_ablation_study(self) -> Dict[str, Any]:
        """
        Runs ablation experiments comparing:
        1. Text-Only pipeline
        2. URL-Only pipeline
        3. Screenshot/OCR-Only pipeline
        4. Text + URL pipeline
        5. Full Multi-Modal Fusion (Orchestrated)
        """
        # Benchmark compound test scenarios
        scenarios = MULTIMODAL_EVALUATION_DATA
        y_true = [s["label"] for s in scenarios]

        ablation_results = {}

        # 1. Text-Only (runs NLP agent alone on text/content)
        pred_text_only = []
        for s in scenarios:
            txt = s["content"] if not s["content"].endswith(".png") else "Dear user your account notice"
            res = self.nlp.analyze(UserInput(content=txt, modality="text"))
            pred_text_only.append(1 if res.modality_score >= 35.0 else 0)
        ablation_results["Text-Only"] = compute_binary_metrics(y_true, pred_text_only)

        # 2. URL-Only (runs URL agent on extracted/provided URLs)
        pred_url_only = []
        for s in scenarios:
            urls = self.nlp.extract_urls(s["content"])
            if urls:
                res = self.url_agent.analyze(UserInput(content=urls[0], modality="url"))
                score = res.modality_score
            else:
                score = 0.0
            pred_url_only.append(1 if score >= 35.0 else 0)
        ablation_results["URL-Only"] = compute_binary_metrics(y_true, pred_url_only)

        # 3. Screenshot/OCR-Only
        pred_ocr_only = []
        for s in scenarios:
            if s["modality"] == "screenshot":
                res = self.orchestrator.ocr.analyze(UserInput(content=s["content"], image_name=s["content"], modality="screenshot"))
                pred_ocr_only.append(1 if res.modality_score >= 20.0 else 0)
            else:
                pred_ocr_only.append(0)
        ablation_results["Screenshot/OCR-Only"] = compute_binary_metrics(y_true, pred_ocr_only)

        # 4. Text + URL
        pred_text_url = []
        for s in scenarios:
            if s["modality"] != "screenshot":
                res = self.orchestrator.analyze(s["content"], modality="text")
                pred_text_url.append(1 if res.risk_score >= 40.0 else 0)
            else:
                # OCR text routed to text+url
                ocr_txt = self.orchestrator.ocr.analyze(UserInput(content=s["content"], image_name=s["content"], modality="screenshot")).metadata.get("extracted_text", "")
                res = self.orchestrator.analyze(ocr_txt, modality="text")
                pred_text_url.append(1 if res.risk_score >= 40.0 else 0)
        ablation_results["Text+URL"] = compute_binary_metrics(y_true, pred_text_url)

        # 5. Full Multi-Modal Fusion (Orchestrated cross-modal + correlation boost)
        pred_full_fusion = []
        for s in scenarios:
            if s["modality"] == "screenshot":
                res = self.orchestrator.analyze(content=s["content"], image_name=s["content"], modality="screenshot")
            else:
                res = self.orchestrator.analyze(content=s["content"], modality="text")
            pred_full_fusion.append(1 if res.risk_score >= 40.0 else 0)
        ablation_results["Full Multi-Modal Fusion"] = compute_binary_metrics(y_true, pred_full_fusion)

        return ablation_results

    def generate_full_report(self) -> Dict[str, Any]:
        text_eval = self.evaluate_text_pipeline()
        url_eval = self.evaluate_url_pipeline()
        ablation = self.run_ablation_study()

        return {
            "text_evaluation": text_eval,
            "url_evaluation": url_eval,
            "ablation_experiments": ablation
        }

if __name__ == "__main__":
    agent = EvaluationAgent()
    print("--- Running Full ScamShield AI Evaluation Suite ---")
    rep = agent.generate_full_report()
    print(f"\n[Text Pipeline] Accuracy: {rep['text_evaluation']['accuracy']*100:.1f}%, F1: {rep['text_evaluation']['f1_score']:.4f}")
    print(f"[URL Pipeline]  Accuracy: {rep['url_evaluation']['accuracy']*100:.1f}%, F1: {rep['url_evaluation']['f1_score']:.4f}")
    print("\n--- Multi-Modal Ablation Results ---")
    for name, m in rep["ablation_experiments"].items():
        print(f"  {name:26}: Precision={m['precision']:.3f} | Recall={m['recall']:.3f} | F1={m['f1_score']:.3f}")
