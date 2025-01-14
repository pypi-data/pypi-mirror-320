from pydantic import BaseModel, Field
from tecton import ProvisionedScalingConfig, Secret, TransformServerGroup

from tecton_gen_ai.api import Agent, Configs, RuntimeVar, tool, get_agent

VERSION = "12_6"
OFFLINE_VERSION = "10_6"


tsg = TransformServerGroup(
    name=f"tsg_{VERSION}",
    description="RT Compute Transform Server Group",
    environment=f"han-ai-ol-{VERSION}",  # The name of the environment from previous step
    scaling_config=ProvisionedScalingConfig(
        desired_nodes=2,
    ),
)

if True:

    class Output(BaseModel):
        answer: str = Field(description="The answer to the user's question")

    Configs(
        llm={
            "model": "openai/gpt-4o-mini",
            "api_key": RuntimeVar(name="OPENAI_API_KEY"),
        },
        default_timeout="15s",
        bfv_config={
            "tecton_materialization_runtime": "1.1.0b11",
            "environment": f"han-ai-{OFFLINE_VERSION}",
        },
        rtfv_config={
            "secrets": {
                "OPENAI_API_KEY": Secret(scope="han-secrets", key="OPENAI_API_KEY_1"),
                "TECTON_API_KEY": Secret(scope="han-secrets", key="TECTON_API_KEY_1"),
            },
        },
        feature_service_config={
            "transform_server_group": tsg,
        },
    ).set_default()

    def should_include(input) -> bool:
        return "how" in input["message"].lower()

    @tool(use_when=should_include)
    def get_company_employee_count(company_name: str) -> int:
        """
        Get the number of employees in a company

        Args:

            company_name: The name of the company

        Returns:

            int: The number of employees in the company, 0 means unknown
        """
        if company_name.lower() == "tecton":
            return 123
        return 0

    story_agent = Agent(
        name="story_agent",
        description="The agent that generates stories from the query (which should be the topic of the story)",
        prompt='You should always start from "Once upon a time" and end with "The end". The story should be at most 50 words',
    )

    def sys_prompt() -> str:
        return "You are a useful agent"

    ra = get_agent(
        name="tecbot",
        workspace="tecdoc",
        api_key=RuntimeVar(name="TECTON_API_KEY"),
    )

    general = Agent(
        name="general_agent",
        description="An agent answering tecton questions",
        prompt=sys_prompt,
        tools=[get_company_employee_count] + ra.export_tools(),
        output_schema=Output,
    )
