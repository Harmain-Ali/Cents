from typing import TypedDict, Optional, List

class Insight(TypedDict):
    impact: str                # "positive", "negative", "neutral"
    text: str
    importance: float          # 0..10, higher = more important
    is_contradiction: Optional[bool]

class SummaryOutput(TypedDict):
    summary: str
    strengths: List[str]
    risks: List[str]
    neutrals: List[str]
    contradictions: List[str]
    recommendation: str
    confidence_label: str
    confidence_score: float