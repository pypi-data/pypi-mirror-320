import pathlib
from datetime import datetime
from enum import Enum
from typing import Literal

import pandas as pd
import pydantic
from tecton import Entity
from tecton.types import Field, String
from tecton_gen_ai.tecton_utils import extraction
from tecton_gen_ai.testing import make_local_source, set_dev_mode

set_dev_mode()


class TranscriptTopic(Enum):
    POLICY_COVERAGE = "policy-coverage"
    CLAIMS_PROCESS = "claims-process"
    DISCOUNTS = "discounts"
    RENEWAL = "renewal"
    CLAIMS_FILING = "claims-filing"
    PREMIUMS = "premiums"
    POLICY_CHANGES = "policy-changes"
    COVERAGE = "coverage"
    ACCIDENT = "accident"
    OTHER = "other"


class TranscriptFeatures(pydantic.BaseModel):
    summary: str = pydantic.Field(description="Summary of the conversation")
    topic: TranscriptTopic
    sentiment: Literal["positive", "neutral", "negative"]


transcript_id = Entity(
    name="transcript", join_keys=[Field(name="transcript_id", dtype=String)]
)


df = pd.read_json(pathlib.Path(__file__).parent / "output.jsonl", lines=True)
src = make_local_source(
    "call_transcripts",
    df,
    description="Call transcripts",
)

extraction_config = [
    {"model": "openai/gpt-4o", "column": "conversation", "schema": TranscriptFeatures}
]
fv = extraction.llm_extraction(src, extraction_config, entities=[transcript_id])

print(
    fv.get_features_in_range(
        start_time=datetime(2024, 1, 1), end_time=datetime(2024, 1, 3)
    ).to_pandas()
)
