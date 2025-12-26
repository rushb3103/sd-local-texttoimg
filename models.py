from dataclasses import dataclass
from typing import Optional

@dataclass
class Job:
    id: str
    prompt: str
    status: str = "queued"   # queued | running | done | error
    result: Optional[dict] = None
    error: Optional[str] = None
