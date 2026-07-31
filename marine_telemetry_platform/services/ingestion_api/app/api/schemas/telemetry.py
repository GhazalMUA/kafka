from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TelemetryBatchAcceptedResponse(BaseModel):
    """
    JSO model that API sends us as a response
    what I expect is smth like this:
    {
    "batch_id": "22222222-2222-4222-8222-222222222222",
    "accepted_events": 3,
    "status": "accepted"
    }

    """

    model_config = ConfigDict(
        extra="forbid",
    )

    batch_id: UUID  # Client can follow-up its request by this uniqe id
    accepted_events: int = Field(ge=1)  # count of accepted events
    status: Literal["accepted"] = "accepted"
