from dataclasses import dataclass, field, asdict
from typing import List, Any, Literal, Optional
from schemas.enums import Channel
from agents import TResponseInputItem, Usage


@dataclass
class User:
    name: str
    id: int
    email: str


@dataclass
class Query:
    sender: str
    subject: str
    body: str
    channel: Channel


@dataclass
class Score:
    score: float
    tags: List[str] = field(default_factory=list)


@dataclass
class QualityScore:
    score_tag: Literal["pass", "needs_improvement", "fail"]
    score_number: int
    feedback: str


@dataclass
class Classification:
    certainty: Score
    complexity: Score
    sentiment: Score


@dataclass
class Category:
    label: str
    confidence: float


@dataclass
class Usages(Usage):
    agent: Optional[str] = None
    cost_estimate: Optional[float] = None


@dataclass
class ClassificationReturn(Classification):
    category: List[Category]


@dataclass
class QueryContext(ClassificationReturn):
    user: Optional[User]


@dataclass
class FailedResponse:
    count: int
    text: str
    score_tag: str
    score_number: int
    feedback: str


@dataclass
class QueryResponse:
    trace_id: str
    trace_link: str
    created_at: str
    duration: str
    user_profile: Optional[User]
    query: Query
    category: List[Category] = field(default_factory=list)
    sentiment: Optional[Score] = None
    certainty: Optional[Score] = None
    complexity: Optional[Score] = None
    response_flag: Optional[str] = None
    response_score: Optional[int] = None
    response: Optional[str] = None
    input_items: List[TResponseInputItem] = field(default_factory=list)
    run_items: List[dict[str, Any]] = field(default_factory=list)
    failed_responses: List[FailedResponse] = field(default_factory=list)
    usages: List[Usages] = field(default_factory=list)
    total_tokens: int = 0
    cost_estimate: float = 0.0
    corrected_response: Optional[str] = None
    is_approved: Optional[bool] = None

    def to_serializable_dict(self):
        data = asdict(self)
        data["query"]["channel"] = str(self.query.channel.value)

        return data
