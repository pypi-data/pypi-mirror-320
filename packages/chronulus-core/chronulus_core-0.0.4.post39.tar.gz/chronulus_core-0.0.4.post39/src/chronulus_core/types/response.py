from pydantic import BaseModel, Field
from typing import List, Optional


class QueuePredictionResponse(BaseModel):
    success: bool
    request_id: str
    prediction_ids: List[str] = Field(default=list())
    message: str = Field(default="")
