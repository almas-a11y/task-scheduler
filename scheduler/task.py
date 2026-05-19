"""Task data model for the Intelligent Task Scheduling System."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

PriorityLevel = Literal["low", "medium", "high"]

PRIORITY_WEIGHTS: dict[str, float] = {
    "low": 33.0,
    "medium": 66.0,
    "high": 100.0,
}


@dataclass
class Task:
    name: str
    deadline: datetime
    duration: float          # estimated hours
    priority_level: PriorityLevel
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    completed: bool = False
    score: float = 0.0       # computed by scheduler

    def days_until_deadline(self) -> float:
        delta = self.deadline - datetime.now()
        return max(0.0, delta.total_seconds() / 86400)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "deadline": self.deadline.isoformat(),
            "duration": self.duration,
            "priority_level": self.priority_level,
            "completed": self.completed,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data["id"],
            name=data["name"],
            deadline=datetime.fromisoformat(data["deadline"]),
            duration=data["duration"],
            priority_level=data["priority_level"],
            completed=data["completed"],
            score=data["score"],
        )

    def __str__(self) -> str:
        status = "[x]" if self.completed else "[ ]"
        return (
            f"{status} {self.name} | "
            f"Due: {self.deadline.strftime('%Y-%m-%d %H:%M')} | "
            f"Duration: {self.duration}h | "
            f"Priority: {self.priority_level} | "
            f"Score: {self.score:.1f}"
        )
