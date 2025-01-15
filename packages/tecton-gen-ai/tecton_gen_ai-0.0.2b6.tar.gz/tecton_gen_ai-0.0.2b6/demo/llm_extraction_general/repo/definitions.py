import os
from datetime import datetime, timedelta

from pydantic import BaseModel, Field
from tecton import FeatureService, Secret

from tecton_gen_ai.api import Configs, llm_extraction
from tecton_gen_ai.testing import make_local_source
from tecton_gen_ai.tecton_utils._tecton_utils import make_entity

VERSION = "9_9"
START = datetime(2024, 1, 1)
END = datetime(2024, 1, 2)


class ExtractName(BaseModel):
    name: str = Field(description="mentioned name")


class ExtractAge(BaseModel):
    age: int = Field(description="mentioned age")


CONFIG = [
    {
        "column": "s1",
        "output_schema": ExtractName,
    },
    {
        "column": "s2",
        "output_schema": ExtractAge,
    },
]


Configs(
    llm={"model": "openai/gpt-4o-mini", "api_key": os.environ["OPENAI_API_KEY"]},
    base_config={
        "secrets": {
            "openai_api_key": Secret(scope="han-secrets", key="OPENAI_API_KEY_1")
        },
        "owner": "tecton",
    },
    bfv_config={
        "tecton_materialization_runtime": "1.1.0b6",
        "environment": f"han-ai-{VERSION}",
    },
).set_default()


src = make_local_source(
    "name_and_age",
    [
        {"user": "u1", "s1": "my name is Jimmy", "s2": "my age is 20", "ts": START},
        {"user": "u2", "s1": "my name is John", "s2": "my age is 30", "ts": START},
    ],
    description="User info",
    timestamp_field="ts",
)

entity = make_entity(user=str)

extraction = llm_extraction(
    source=src,
    extraction_config=CONFIG,
    entities=[entity],
    timestamp_field="ts",
    feature_start_time=START,
    max_backfill_interval=timedelta(days=1000),
)

service = FeatureService(
    name="llm_extraction",
    features=[extraction],
)
