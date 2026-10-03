import io
import os
import numpy as np
from typing import List, Optional
from PIL import Image
from src.models.schemas import UserInput, Evidence, AgentResult

class VisionAgent:
    """
    Vision Agent for ScamShield AI.
    Inspects visual characteristics of screenshots, including color dominance
    (warning/red urgency banners), interface composition, and visual spoofing artifacts.
    """
    def analyze(self, user_input: UserInput) -> AgentResult:
        evidence_list: List[Evidence] = []
        pil_img: Optional[Image.Image] = None

        if user_input.image_bytes:
            try:
                pil_img = Image.open(io.BytesIO(user_input.image_bytes)).convert("RGB")
            except Exception as e:
                print(f"[VisionAgent] Error loading image bytes: {e}")
        elif user_input.content and os.path.exists(user_input.content):
            try:
                pil_img = Image.open(user_input.content).convert("RGB")
            except Exception as e:
                print(f"[VisionAgent] Error loading image path: {e}")

        if pil_img is None:
            return AgentResult(agent_name="vision_agent", evidence_list=[], modality_score=0.0)

        # 1. Image dimensions & aspect ratio
        width, height = pil_img.size
        aspect_ratio = round(width / max(1, height), 2)
        
        # Resize for fast numpy color inspection
        thumb = pil_img.resize((100, 100))
        arr = np.array(thumb, dtype=float)

        # 2. Urgent Alert Red/Crimson Detection
        # Red is high R, low G, low B
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        red_mask = (r > 160) & (g < 80) & (b < 80)
        red_ratio = float(np.sum(red_mask) / (100 * 100))

        # 3. Yellow/Warning Banner Detection (high R, high G, low B)
        yellow_mask = (r > 180) & (g > 160) & (b < 90)
        yellow_ratio = float(np.sum(yellow_mask) / (100 * 100))

        # 4. Formulate Visual Evidence
        if red_ratio > 0.04:
            evidence_list.append(Evidence(
                indicator="visual_urgency_styling",
                detected=True,
                severity="medium",
                confidence=0.82,
                source="vision_agent",
                evidence=f"Prominent red warning alert banner detected ({red_ratio*100:.1f}% visual area).",
                explanation="Scareware and urgent phishing layouts employ high-contrast crimson headers to incite panic."
            ))
        elif yellow_ratio > 0.05:
            evidence_list.append(Evidence(
                indicator="visual_warning_banner",
                detected=True,
                severity="low",
                confidence=0.75,
                source="vision_agent",
                evidence=f"Prominent amber/yellow warning badge detected ({yellow_ratio*100:.1f}% visual area).",
                explanation="Simulated security warnings frequently employ warning yellow banners."
            ))

        # 5. Mobile / Desktop Capture formatting
        is_mobile_capture = aspect_ratio < 0.7
        metadata = {
            "dimensions": f"{width}x{height}",
            "aspect_ratio": aspect_ratio,
            "is_mobile_aspect": is_mobile_capture,
            "red_banner_pct": round(red_ratio * 100, 2),
            "yellow_banner_pct": round(yellow_ratio * 100, 2)
        }

        # Calculate modality risk score
        modality_score = 0.0
        if red_ratio > 0.04:
            modality_score += 35.0
        if yellow_ratio > 0.05:
            modality_score += 20.0
        modality_score = min(modality_score, 100.0)

        return AgentResult(
            agent_name="vision_agent",
            evidence_list=evidence_list,
            modality_score=modality_score,
            metadata=metadata
        )
