from datetime import datetime
from typing import Tuple, Dict, Optional
import re

class GKEngine:
    """
    Offline General Knowledge engine.
    Handles system queries (time, date) and a set of trusted static facts.
    """

    def __init__(self):
        raw_facts = {
            "capital of india": "New Delhi",
            "pm of india": "Narendra Modi",
            "president of india": "Droupadi Murmu",
            "largest planet": "Jupiter",
            "speed of light": "299,792,458 m/s",
        }
        
        self._facts = {
            self._normalize_key(k): v
            for k, v in raw_facts.items()
        }

    def answer(self, query: str) -> Tuple[Optional[str], float, Dict]:
        """
        Attempt to answer a query using internal knowledge.
        Returns: (answer, confidence, metadata)
        """
        if not query or not isinstance(query, str):
            return None, 0.0, {}

        q = self._normalize_key(query)

        # Handle Time Queries
        if self._is_time_query(q):
            now = datetime.now().astimezone()
            return (
                now.strftime("%I:%M %p %Z").strip(),
                0.95,
                self._build_metadata("time")
            )

        # Handle Date Queries
        if self._is_date_query(q):
            today = datetime.now().astimezone()
            return (
                today.strftime("%A, %d %B %Y"),
                0.95,
                self._build_metadata("date")
            )

        # Handle Static GK Facts
        if q in self._facts:
            return (
                self._facts[q],
                0.90,
                self._build_metadata("static_fact")
            )
            
        # Try removing common question prefixes
        clean_q = re.sub(r"^(what|who|where)('s| is| are| was| were)?( the)?\s+", "", q).strip()
        
        if clean_q in self._facts:
             return (
                self._facts[clean_q],
                0.90, 
                self._build_metadata("static_fact")
            )

        return None, 0.0, {}

    def _normalize_key(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    def _build_metadata(self, category: str) -> Dict:
        return {
            "well_known": True,
            "category": category,
            "source": "gk"
        }

    def _is_time_query(self, q: str) -> bool:
        if q in {"time", "current time", "time now"}:
            return True
            
        if re.search(r"^what time is it", q):
            return True
            
        if re.search(r"^what is the (current )?time", q):
            return True
            
        return False

    def _is_date_query(self, q: str) -> bool:
        if q in {"date", "today", "current date", "what is today"}:
            return True
            
        if re.search(r"^what('s| is) (the )?date", q):
            return True
            
        if re.search(r"^what day is (it|today)", q):
            return True
            
        return False