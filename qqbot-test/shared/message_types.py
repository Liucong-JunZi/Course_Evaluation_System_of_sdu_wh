from dataclasses import dataclass
from typing import Optional, Dict, Any
import json

@dataclass
class Message:
    session_id: str
    content: str
    msg_type: str = "chat"
    metadata: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        return json.dumps({
            "session_id": self.session_id,
            "content": self.content,
            "msg_type": self.msg_type,
            "metadata": self.metadata
        })

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls(**data)