from dataclasses import dataclass, field
from typing import Literal
from pydantic import BaseModel, Field

Section = Literal['paddle-boards', 'shelving', 'returns-and-warranty', 'shipping', 'other']

@dataclass
class Incoming:
    key: str
    sender: str
    subject: str
    body: str
    message_id: str
    references: list[str] = field(default_factory=list)
    attachments: bool = False
    automatic: bool = False
    received_at: str = ''

class Classification(BaseModel):
    section: Section
    needs_human: bool
    reason: str

class ProductIssue(BaseModel):
    product: Literal['board','shelf','unknown'] = 'unknown'
    problem: Literal['accessory','air_loss','seam','hardware','panels','frame','finish','unknown'] = 'unknown'
    order: str = ''
    delivery_days: int | None = Field(default=None,ge=0)
    valve_checked: bool = False
    parts: list[str] = Field(default_factory=list)

class Draft(BaseModel):
    text: str = Field(max_length=12000)
    sufficient: bool
    needs_human: bool
    reason: str
    sources: list[str]
    proposed_action: str = ''
    issue: ProductIssue | None = None

class Decision(BaseModel):
    category: str
    state: Literal['review', 'escalated', 'skipped']
    draft: str = ''
    reason: str
    sources: list[str] = Field(default_factory=list)
    proposed_action: str = ''
    input_tokens: int = 0
    output_tokens: int = 0
    engine: str = 'demo'
