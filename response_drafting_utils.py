from pydantic import BaseModel
from pydantic import Field
from typing import Optional

    
class ResponseDraftingInput(BaseModel):
    ticket_id: str = Field(required=True, description="The Id of ticket you are drafting")
    query: str = Field(required=True, description="Customer issue Text")
    policy: Optional[str] = Field(required=False, description="Relevant policy text to follow strictly")
    previous_record: Optional[tuple] = Field(required=False, description="Similar resolved tickets for reference")


class ResponseDraftingOutput(BaseModel):
    ticket_id: str = Field(required=True, description="The Id of ticket you are drafting")
    reply: str = Field(required=True, description="Policy-compliant reply draft for human review")
    tone: str = Field(required=True, description="Tone of response: polite, neutral, apologetic")
    confidence: float = Field(required=True, description="How much You are confident about your draft output")
    used_policy: str = Field(default=None, required=False, description="Policy Reference used in Drafting")
    used_reference_ticket_id: Optional[str] = Field(default=None, required=False, description="id of previous solved Ticket used as reference")