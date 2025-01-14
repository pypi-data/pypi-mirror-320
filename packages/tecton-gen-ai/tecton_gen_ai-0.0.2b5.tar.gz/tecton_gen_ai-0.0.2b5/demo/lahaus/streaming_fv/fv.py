from datetime import datetime, timedelta

from tecton import (
    Aggregate,
    Entity,
    FeatureService,
    PushConfig,
    StreamSource,
    stream_feature_view,
)
from tecton.types import Field, Float64, Int64, String, Timestamp
from tecton.aggregation_functions import last_distinct

user = Entity(
    name="user_id", join_keys=[Field("user_id", String)], description="User id"
)


def create_mention(
    entity,
    field,
    function,
    agg_function="last",
    time_window=timedelta(days=30),
    ingestion_description=None,
    serve_description=None,
    name=None,
):
    col_name = function + "_" + field.name
    name = "mention_of_" + (name or col_name)

    mention = StreamSource(
        name=name,
        stream_config=PushConfig(),
        schema=[
            Field("user_id", String),
            Field("timestamp", Timestamp),
            field,
        ],
        description=ingestion_description,
    )

    @stream_feature_view(
        name=name,
        source=mention,
        entities=[entity],
        mode="pandas",
        timestamp_field="timestamp",
        features=[
            Aggregate(
                input_column=field,
                function=agg_function,
                time_window=time_window,
                name=name,
            ),
        ],
        online=True,
        offline=True,
        feature_start_time=datetime(2024, 1, 1),
        batch_schedule=timedelta(days=1),
        description=serve_description,
    )
    def fv(df):
        return df

    return fv


budget_min = create_mention(
    entity=user,
    field=Field("budget", Float64),
    function="min",
    ingestion_description="User's mention of minimum budget",
    serve_description="User's minimum budget in the last 30 days",
)

budget_max = create_mention(
    entity=user,
    field=Field("budget", Float64),
    function="max",
    ingestion_description="User's mention of maximum budget",
    serve_description="User's maximum budget in the last 30 days",
)

bedroom_min = create_mention(
    entity=user,
    field=Field("bedroom_count", Int64),
    function="min",
    ingestion_description="User's mention of minimum bedroom count",
    serve_description="User's minimum bedroom count in the last 30 days",
)

bedroom_max = create_mention(
    entity=user,
    field=Field("bedroom_count", Int64),
    function="max",
    ingestion_description="User's mention of maximum bedroom count",
    serve_description="User's maximum bedroom count in the last 30 days",
)

area_min = create_mention(
    entity=user,
    field=Field("area", Float64),
    function="min",
    ingestion_description="User's mention of minimum area",
    serve_description="User's minimum area in the last 30 days",
)

area_max = create_mention(
    entity=user,
    field=Field("area", Float64),
    function="max",
    ingestion_description="User's mention of maximum area",
    serve_description="User's maximum area in the last 30 days",
)

other = create_mention(
    entity=user,
    field=Field("miscellaneous_preference", String),
    function="all",
    agg_function=last_distinct(5),
    ingestion_description="User's miscellaneous preferences that are not budget, bedroom count, or area",
    serve_description="User's miscellaneous preferences that are not budget, bedroom count, or area",
    name="miscellaneous_preference",
)


user_preference = FeatureService(
    name="user_preference",
    description="User's preference on budget and room count",
    features=[
        budget_min,
        budget_max,
        bedroom_min,
        bedroom_max,
        area_min,
        area_max,
        other,
    ],
)
